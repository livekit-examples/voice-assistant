LiveKit docs › Agent Frontends › Agents UI Components › Overview

---

# Agents UI components

> Polished Shadcn components for rapid development of voice agent frontends.

![Screenshot of Agents UI components used in our agent starter React app](/images/agents/start/frontend/agent-starter-react-screenshot-dark.png)

## Overview

[Agents UI](https://docs.livekit.io/reference/components/agents-ui.md) is a component library built on top of [Shadcn](https://ui.shadcn.com/) and [AI Elements](https://ai-sdk.dev/elements) to accelerate the creation of agentic applications built with LiveKit's realtime platform. It provides pre-built components for controlling IO, managing sessions, rendering transcripts, visualizing audio streams, and more.

## Installation

You can install Agents UI components using the Shadcn CLI. First, set up shadcn in your project and add the Agents UI registry:

```bash
npx shadcn@latest init
npx shadcn@latest registry add @agents-ui

```

Then install components individually:

```bash
npx shadcn@latest add @agents-ui/{component-name}

```

Or install every Agents UI component at once with:

```bash
npx shadcn@latest add @agents-ui/all

```

> ℹ️ **Note**
> 
> The `nextjs-api-token-route` helper is excluded from `@agents-ui/all`. Add it separately if you need it for your Next JS application.

After installation, components are available in your project's `components/agents-ui` directory with full source code that you can customize.

- **[Agents UI reference](https://docs.livekit.io/reference/components/agents-ui.md)**: Complete reference documentation for Agents UI components.

- **[GitHub repository](https://github.com/livekit/components-js/tree/main/packages/shadcn)**: Open source Agents UI component code.

## Other UI component SDKs

LiveKit also provides component libraries for other frameworks. While these are not agents-specific, they include useful components for building realtime applications:

| Framework | Description |
| **[React components](https://docs.livekit.io/reference/components/react.md)** | Low-level React components and hooks for building realtime audio and video applications with LiveKit's platform primitives. |
| **[Swift components](https://livekit.github.io/components-swift/documentation/livekitcomponents)** | SwiftUI components for iOS, macOS, visionOS, and tvOS applications with native platform integration. |
| **[Android components](https://docs.livekit.io/reference/components/android.md)** | Jetpack Compose components for Android applications with Material Design integration. |
| **[Flutter components](https://github.com/livekit/components-flutter)** | Flutter widgets for cross-platform mobile and desktop applications. |

## In this section

Agents UI organizes components into the following categories. Each category page explains what the components do, when to use them, and includes live previews.

| Category | What it includes | When to use |
| **[Media controls](https://docs.livekit.io/frontends/agents-ui/media-controls.md)** | AgentControlBar, AgentTrackControl, AgentTrackToggle, AgentDisconnectButton, StartAudioButton | Give users control over microphone, camera, session disconnect, and browser audio playback. |
| **[Audio visualizer](https://docs.livekit.io/frontends/agents-ui/audio-visualizer.md)** | AgentAudioVisualizerBar, Grid, Radial, Wave, Aura | Give your voice agent a visual presence with animated visualizations driven by audio data and agent state. |
| **[Chat components](https://docs.livekit.io/frontends/agents-ui/chat.md)** | AgentChatTranscript, AgentChatIndicator | Display realtime conversation transcripts, text messages, and typing indicators. |

---

This document was rendered at 2026-09-12T08:47:14.671Z.
For the latest version of this document, see [https://docs.livekit.io/frontends/agents-ui.md](https://docs.livekit.io/frontends/agents-ui.md).

To explore all LiveKit documentation, see [llms.txt](https://docs.livekit.io/llms.txt).