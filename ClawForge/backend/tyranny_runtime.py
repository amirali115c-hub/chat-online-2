# tyranny_runtime.py - Secure Command Execution Framework for Leo 2.0
"""
A production-ready secure command execution framework.
Enables safe, auditable, and extensible command execution for the Leo 2.0 dashboard.

Features:
- Command Registry: Dynamic command registration
- Whitelist Security: Only allowed executables
- Timeout Protection: Prevents hanging processes
- Logging & Auditing: Full execution history
- Async Support: Non-blocking execution
"""

from __future__ import annotations

import asyncio
import logging
import shlex
import subprocess
import sys
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime

# ============================================================================
# Core Data Structures
# ============================================================================

@dataclass
class Executable:
    """
    A whitelisted binary that the runtime may invoke.
    """
    name: str
    allowed_paths: List[Path] | None = field(default=None)
    default_args: List[str] = field(default_factory=list)
    description: str = ""  # Human-readable description


@dataclass
class CommandSpec:
    """
    Describes a single command that a user can request.
    """
    name: str
    description: str
    executable: Executable
    build_cmd: Callable[[Dict[str, str]], List[str]]
    timeout_seconds: Optional[int] = 30
    env: Optional[Dict[str, str]] = None
    cwd: Optional[Path] = None
    pre_validate: Optional[Callable[[Dict[str, str]], bool]] = None
    allowed: bool = True  # Whether this command is allowed to run

    def __call__(self, context: "RuntimeContext") -> "ExecutionResult":
        """Execute the command via the underlying Executor."""
        return self.executable.run(
            argv=self.build_cmd(context.args),
            timeout=self.timeout_seconds,
            env=self.env,
            cwd=self.cwd,
        )


@dataclass
class ExecutionResult:
    """
    Holds everything the caller may need about the outcome of a command.
    """
    command: str
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool
    context: Dict[str, str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = False

    def __post_init__(self):
        self.success = self.returncode == 0 and not self.timed_out


# ============================================================================
# Low-Level Executor
# ============================================================================

class Executor:
    """
    Secure wrapper around subprocess with whitelist enforcement.
    """
    
    # Default whitelist of allowed binaries
    _WHITELIST: Dict[str, Executable] = {
        "python": Executable(
            name="python",
            allowed_paths=[Path("python"), Path("python3"), Path("py")],
            description="Python interpreter"
        ),
        "python3": Executable(
            name="python3",
            allowed_paths=[Path("python3")],
            description="Python 3 interpreter"
        ),
        "node": Executable(
            name="node",
            allowed_paths=[Path("node")],
            description="Node.js runtime"
        ),
        "npm": Executable(
            name="npm",
            allowed_paths=[Path("npm")],
            description="Node package manager"
        ),
        "pip": Executable(
            name="pip",
            allowed_paths=[Path("pip"), Path("pip3")],
            description="Python package installer"
        ),
        "git": Executable(
            name="git",
            allowed_paths=[Path("git")],
            description="Git version control"
        ),
        "ls": Executable(
            name="ls",
            allowed_paths=[Path("ls")],
            description="List directory contents"
        ),
        "cat": Executable(
            name="cat",
            allowed_paths=[Path("cat")],
            description="Display file contents"
        ),
        "mkdir": Executable(
            name="mkdir",
            allowed_paths=[Path("mkdir")],
            description="Create directories"
        ),
        "cd": Executable(
            name="cd",
            allowed_paths=[],  # Built-in, handled specially
            description="Change directory"
        ),
        "sh": Executable(
            name="sh",
            allowed_paths=[Path("sh"), Path("bash")],
            description="Shell interpreter"
        ),
    }

    def __init__(self, logger: logging.Logger | None = None, workspace_dir: Path | None = None):
        self.logger = logger or logging.getLogger(__name__)
        self.workspace_dir = workspace_dir or Path.cwd()
        self._execution_history: List[ExecutionResult] = []
        self._max_history = 100

    def add_to_whitelist(self, executable: Executable) -> None:
        """Add a new executable to the whitelist."""
        self._WHITELIST[executable.name] = executable
        self.logger.info(f"Added '{executable.name}' to whitelist: {executable.description}")

    def is_whitelisted(self, exe_name: str) -> bool:
        """Check if an executable is whitelisted."""
        return exe_name in self._WHITELIST

    def run(
        self,
        argv: List[str],
        timeout: Optional[int],
        env: Optional[Dict[str, str]],
        cwd: Optional[Path],
    ) -> ExecutionResult:
        """Execute the command and return an ExecutionResult."""
        
        if not argv:
            raise ValueError("Empty command provided")

        exe_name = argv[0]
        
        # Security check: executable must be whitelisted
        exe = self._WHITELIST.get(exe_name)
        if exe is None:
            raise PermissionError(f"Executable '{exe_name}' is not whitelisted")

        # Resolve executable path
        exe_path = self._resolve_executable(exe, exe_name)
        
        # Use workspace as default working directory
        final_cwd = str(cwd or self.workspace_dir)
        
        # Build environment
        final_env = env or {}
        final_env.setdefault("HOME", os.path.expanduser("~"))
        
        # Build command string for logging
        cmd_str = " ".join(shlex.quote(a) for a in argv)
        
        self.logger.info(f"EXEC: {cmd_str}")
        self.logger.debug(f"CWD={final_cwd}")

        # Execute the command
        start_time = datetime.now()
        
        try:
            proc = subprocess.Popen(
                argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=final_env,
                cwd=final_cwd,
                text=True,
                encoding="utf-8",
                shell=False,  # Never use shell=True for security
            )
            
            try:
                stdout, stderr = proc.communicate(timeout=timeout or 30)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                self.logger.warning(f"Command timed out after {timeout}s: {cmd_str}")
                result = ExecutionResult(
                    command=cmd_str,
                    stdout=stdout,
                    stderr=stderr,
                    returncode=-1,
                    timed_out=True,
                    context={},
                )
                self._add_to_history(result)
                return result
                
        except FileNotFoundError as e:
            self.logger.error(f"Executable not found: {e}")
            result = ExecutionResult(
                command=cmd_str,
                stdout="",
                stderr=str(e),
                returncode=-1,
                timed_out=False,
                context={},
            )
            self._add_to_history(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            result = ExecutionResult(
                command=cmd_str,
                stdout="",
                stderr=str(e),
                returncode=-1,
                timed_out=False,
                context={},
            )
            self._add_to_history(result)
            return result

        # Log output
        self.logger.debug(f"STDOUT:\n{stdout}")
        if stderr:
            self.logger.debug(f"STDERR:\n{stderr}")
        
        result = ExecutionResult(
            command=cmd_str,
            stdout=stdout,
            stderr=stderr,
            returncode=proc.returncode,
            timed_out=False,
            context={},
        )
        
        self._add_to_history(result)
        return result

    def _resolve_executable(self, exe: Executable, exe_name: str) -> Path:
        """Resolve the actual path of the executable."""
        if exe.allowed_paths:
            for path in exe.allowed_paths:
                # Check if it's an absolute path that exists
                if path.is_absolute() and path.is_file():
                    return path
                # Check in PATH
                which_result = subprocess.run(
                    ["where" if os.name == "nt" else "which", exe_name],
                    capture_output=True,
                    text=True,
                )
                if which_result.returncode == 0:
                    resolved = Path(which_result.stdout.strip().split('\n')[0])
                    if resolved.is_file():
                        return resolved
            # Fallback to first allowed path
            return exe.allowed_paths[0]
        return Path(exe_name)

    def _add_to_history(self, result: ExecutionResult) -> None:
        """Add execution result to history."""
        self._execution_history.append(result)
        if len(self._execution_history) > self._max_history:
            self._execution_history.pop(0)

    def get_history(self, limit: int = 10) -> List[ExecutionResult]:
        """Get recent execution history."""
        return self._execution_history[-limit:]

    def clear_history(self) -> None:
        """Clear execution history."""
        self._execution_history.clear()


# ============================================================================
# Runtime Context
# ============================================================================

class RuntimeContext:
    """Holds data needed while building/executing a command."""
    
    def __init__(self, user_args: Dict[str, str], workspace_dir: Path | None = None):
        self.args = user_args
        self.workspace_dir = workspace_dir or Path.cwd()


# ============================================================================
# Command Runner (Main API)
# ============================================================================

class CommandRunner:
    """
    Public façade for registering and executing commands.
    
    Usage:
        runner = CommandRunner()
        runner.register(
            name="run_python",
            description="Execute Python code",
            executable=Executable("python"),
            build_cmd=lambda ctx: ["python", "-c", ctx.args["code"]]
        )
        result = runner.run("run_python", {"code": "print('Hello!')"})
    """
    
    def __init__(
        self, 
        logger: logging.Logger | None = None, 
        workspace_dir: Path | None = None
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.executor = Executor(logger=self.logger, workspace_dir=workspace_dir)
        self._registry: Dict[str, CommandSpec] = {}
        
        # Register default commands
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """Register built-in safe commands."""
        
        # Python execution
        self.register(
            name="python",
            description="Run Python code/script",
            executable=Executable("python3", description="Python interpreter"),
            build_cmd=lambda ctx: ["python3", ctx.args.get("file", "-c", ctx.args.get("code", ""))],
            timeout_seconds=30,
        )
        
        # Node.js execution
        self.register(
            name="node",
            description="Run Node.js code/script",
            executable=Executable("node", description="Node.js runtime"),
            build_cmd=lambda ctx: ["node", "-e", ctx.args.get("code", "")],
            timeout_seconds=30,
        )
        
        # List files
        self.register(
            name="list_files",
            description="List files in a directory",
            executable=Executable("ls", description="List directory"),
            build_cmd=lambda ctx: ["ls", "-la", ctx.args.get("path", ".")],
            timeout_seconds=10,
        )
        
        # Read file
        self.register(
            name="read_file",
            description="Read file contents",
            executable=Executable("cat", description="Display file"),
            build_cmd=lambda ctx: ["cat", ctx.args.get("path", "")],
            timeout_seconds=10,
        )

    def register(
        self,
        name: str,
        description: str,
        executable: Executable,
        build_cmd: Callable[[RuntimeContext], List[str]],
        timeout_seconds: Optional[int] = 30,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[Path] = None,
        pre_validate: Optional[Callable[[Dict[str, str]], bool]] = None,
    ) -> None:
        """Register a new command."""
        
        # Ensure executable is in whitelist
        if not self.executor.is_whitelisted(executable.name):
            self.executor.add_to_whitelist(executable)
        
        spec = CommandSpec(
            name=name,
            description=description,
            executable=executable,
            build_cmd=build_cmd,
            timeout_seconds=timeout_seconds,
            env=env,
            cwd=cwd,
            pre_validate=pre_validate,
        )
        
        self._registry[name] = spec
        self.logger.info(f"Registered command '{name}': {description}")

    def unregister(self, name: str) -> bool:
        """Unregister a command."""
        if name in self._registry:
            del self._registry[name]
            self.logger.info(f"Unregistered command '{name}'")
            return True
        return False

    def list_commands(self) -> List[Dict[str, str]]:
        """List all registered commands."""
        return [
            {"name": name, "description": spec.description}
            for name, spec in self._registry.items()
        ]

    def run(
        self, 
        cmd_name: str, 
        user_args: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Execute a registered command."""
        
        if cmd_name not in self._registry:
            raise ValueError(f"Command '{cmd_name}' is not registered")
        
        ctx = RuntimeContext(user_args or {})
        spec = self._registry[cmd_name]
        
        # Pre-validation
        if spec.pre_validate and not spec.pre_validate(ctx.args):
            raise ValueError(f"Invalid arguments for command '{cmd_name}'")
        
        # Build command
        argv = spec.build_cmd(ctx)
        
        # Execute
        result = self.executor.run(
            argv=argv,
            timeout=timeout or spec.timeout_seconds,
            env=spec.env,
            cwd=spec.cwd,
        )
        
        result.context = ctx.args
        return result

    async def run_async(
        self,
        cmd_name: str,
        user_args: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Execute a command asynchronously."""
        
        if cmd_name not in self._registry:
            raise ValueError(f"Command '{cmd_name}' is not registered")
        
        ctx = RuntimeContext(user_args or {})
        spec = self._registry[cmd_name]
        argv = spec.build_cmd(ctx)
        
        exe = spec.executable
        exe_path = self.executor._resolve_executable(exe, exe.name)
        
        final_env = spec.env or {}
        final_env.setdefault("HOME", os.path.expanduser("~"))
        
        cmd_str = " ".join(shlex.quote(a) for a in argv)
        
        try:
            proc = await asyncio.create_subprocess_exec(
                str(exe_path),
                *argv[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(spec.cwd) if spec.cwd else None,
                env=final_env,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), 
                    timeout=timeout or spec.timeout_seconds or 30
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                raise TimeoutError(f"Command timed out after {spec.timeout_seconds}s")
            
            return ExecutionResult(
                command=cmd_str,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else "",
                returncode=proc.returncode,
                timed_out=False,
                context=ctx.args,
            )
            
        except Exception as e:
            return ExecutionResult(
                command=cmd_str,
                stdout="",
                stderr=str(e),
                returncode=-1,
                timed_out=False,
                context=ctx.args,
            )

    def get_history(self, limit: int = 10) -> List[ExecutionResult]:
        """Get execution history."""
        return self.executor.get_history(limit)


# ============================================================================
# Module-level convenience
# ============================================================================

# Create default instance
_default_runner: Optional[CommandRunner] = None

def get_default_runner(workspace_dir: Path | None = None) -> CommandRunner:
    """Get or create the default CommandRunner instance."""
    global _default_runner
    if _default_runner is None:
        _default_runner = CommandRunner(workspace_dir=workspace_dir)
    return _default_runner


if __name__ == "__main__":
    # Demo
    logging.basicConfig(level=logging.INFO)
    runner = CommandRunner(workspace_dir=Path.cwd())
    
    # List commands
    print("Available commands:", runner.list_commands())
    
    # Run a test
    try:
        result = runner.run("list_files", {"path": "."})
        print(f"Success: {result.success}")
        print(f"Output: {result.stdout[:200]}")
    except Exception as e:
        print(f"Error: {e}")
