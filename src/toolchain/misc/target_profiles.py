"""Per-target output/build/run contracts for pytra-cli.

Provides the minimal profile data needed by parity check tools.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TargetProfile:
    target: str
    extension: str
    build_driver: str
    fixed_output_name: str
    allow_codegen_opt: bool
    runner_needs: tuple[str, ...]


_TARGET_PROFILES: dict[str, TargetProfile] = {
    "cpp": TargetProfile(target="cpp", extension=".cpp", build_driver="cpp_make", fixed_output_name="", allow_codegen_opt=True, runner_needs=("python", "make", "g++")),
    "rs": TargetProfile(target="rs", extension=".rs", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "rustc")),
    "cs": TargetProfile(target="cs", extension=".cs", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "mcs", "mono")),
    "js": TargetProfile(target="js", extension=".js", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "node")),
    "ts": TargetProfile(target="ts", extension=".ts", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "node", "npx")),
    "go": TargetProfile(target="go", extension=".go", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "go")),
    "java": TargetProfile(target="java", extension=".java", build_driver="noncpp", fixed_output_name="Main.java", allow_codegen_opt=False, runner_needs=("python", "javac", "java")),
    "swift": TargetProfile(target="swift", extension=".swift", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "swiftc")),
    "kotlin": TargetProfile(target="kotlin", extension=".kt", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "kotlinc", "java")),
    "scala": TargetProfile(target="scala", extension=".scala", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "scala-cli")),
    "lua": TargetProfile(target="lua", extension=".lua", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "lua")),
    "ruby": TargetProfile(target="ruby", extension=".rb", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "ruby")),
    "php": TargetProfile(target="php", extension=".php", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "php")),
    "julia": TargetProfile(target="julia", extension=".jl", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "julia")),
    "nim": TargetProfile(target="nim", extension=".nim", build_driver="noncpp", fixed_output_name="main.nim", allow_codegen_opt=False, runner_needs=("python", "nim")),
    "dart": TargetProfile(target="dart", extension=".dart", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "dart")),
    "zig": TargetProfile(target="zig", extension=".zig", build_driver="noncpp", fixed_output_name="", allow_codegen_opt=False, runner_needs=("python", "zig")),
}


def get_target_profile(target: str) -> TargetProfile:
    profile = _TARGET_PROFILES.get(target)
    if isinstance(profile, TargetProfile):
        return profile
    raise RuntimeError("unsupported target profile: " + target)


def list_parity_targets() -> list[str]:
    return ["cpp", "rs", "cs", "js", "ruby", "lua", "php", "ts", "go", "java", "swift", "kotlin", "scala", "julia", "nim", "dart", "zig"]
