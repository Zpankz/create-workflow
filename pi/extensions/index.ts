import type { ExtensionAPI } from "pi";

export default function createWorkflowExtension(pi: ExtensionAPI) {
  pi.on("session_start", (_event) => {
    // Stub: generate-hooks skill extends this for target projects
  });

  pi.on("tool_result", (_event) => {
    // Stub: generate-hooks skill extends this for target projects
  });

  pi.on("session_shutdown", (_event) => {
    // Stub: generate-hooks skill extends this for target projects
  });
}
