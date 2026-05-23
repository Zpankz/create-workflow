"""
create-workflow Hermes plugin.

Registers skills from the skills/ directory and provides hook stubs
that the generate-hooks skill can extend for target projects.
"""

import os
import glob

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(PLUGIN_DIR, "skills")


def register(ctx):
    """Hermes plugin entry point."""

    for skill_dir in sorted(glob.glob(os.path.join(SKILLS_DIR, "*/"))):
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if os.path.isfile(skill_md):
            skill_name = os.path.basename(os.path.normpath(skill_dir))
            ctx.register_skill(
                name=skill_name,
                path=skill_md,
            )

    ctx.register_hook("post_tool_call", _post_tool_call)
    ctx.register_hook("on_session_end", _on_session_end)


def _post_tool_call(event):
    """Stub hook — extended by generate-hooks for target projects."""
    pass


def _on_session_end(event):
    """Stub hook — extended by generate-hooks for target projects."""
    pass
