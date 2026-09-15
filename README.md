# Agent Starter for React

This is a starter template for [LiveKit Agents](https://docs.livekit.io/agents) that provides a simple voice interface using [Agents UI](https://livekit.io/ui) components and [LiveKit JavaScript SDK](https://github.com/livekit/client-sdk-js). It supports [voice](https://docs.livekit.io/agents/start/voice-ai), [transcriptions](https://docs.livekit.io/agents/build/text/), and [virtual avatars](https://docs.livekit.io/agents/integrations/avatar).

Also available for:
[Android](https://github.com/livekit-examples/agent-starter-android) • [Flutter](https://github.com/livekit-examples/agent-starter-flutter) • [Swift](https://github.com/livekit-examples/agent-starter-swift) • [React Native](https://github.com/livekit-examples/agent-starter-react-native)

<picture>
  <source srcset="./.github/assets/readme-hero-dark.webp" media="(prefers-color-scheme: dark)">
  <source srcset="./.github/assets/readme-hero-light.webp" media="(prefers-color-scheme: light)">
  <img src="./.github/assets/readme-hero-light.webp" alt="App screenshot">
</picture>

### Features:

- Real-time voice interaction with LiveKit Agents
- Camera video streaming support
- Screen sharing capabilities
- Multiple audio visualizer styles (`bar`, `grid`, `radial`, `wave`, `aura`)
- Virtual avatar integration
- Light/dark theme switching with system preference detection
- Customizable branding, colors, and UI text

This template is built with Next.js and is free for you to use or modify as you see fit.

## Getting started

Clone this template, install dependencies, and run the app:

```bash
git clone https://github.com/livekit-examples/agent-starter-react.git
cd agent-starter-react
pnpm install
pnpm dev
```

Then open http://localhost:3000 in your browser.

The app is configured to connect to the LiveKit homepage agent by default, which you can also try at [livekit.com](https://www.livekit.com). That agent takes voice and text input only, so video and screen sharing are hidden until you point the app at your own agent (see [Connect to your agent](#connect-to-your-agent)).

## Connect to your agent

To switch from the default agent to your own, you first need a LiveKit agent to speak with. For a no-code setup, use the [Agent Builder](https://docs.livekit.io/agents/start/builder/). For more customization, try our starter agent for [Python](https://github.com/livekit-examples/agent-starter-python), [Node.js](https://github.com/livekit-examples/agent-starter-node), or [create your own from scratch](https://docs.livekit.io/agents/start/voice-ai/).

Second, you need a token server. For development, the easiest option is the [development token server](https://docs.livekit.io/frontends/build/authentication/development-token-server/): switch on the **Development token server** toggle on your project's [Settings](https://cloud.livekit.io/projects/p_/settings/project) page in LiveKit Cloud and copy the **Token server ID** below it. Then copy `.env.example` to `.env.local` and fill it in:

```env
LIVEKIT_TOKEN_SERVER_ID=<your-token-server-id>
```

Alternatively, use the token endpoint included in this app at [`app/api/token/route.ts`](./app/api/token/route.ts). It needs your project's LiveKit credentials in `.env.local`, which the LiveKit CLI fills in for you when it clones the template:

```bash
lk app create --template agent-starter-react
```

Or copy them from your project's Settings page yourself:

```env
LIVEKIT_URL=wss://<project-subdomain>.livekit.cloud
LIVEKIT_API_KEY=<your_api_key>
LIVEKIT_API_SECRET=<your_api_secret>
```

Leave `AGENT_NAME` blank for automatic dispatch, or set it to your agent's name for [explicit dispatch](https://docs.livekit.io/agents/server/agent-dispatch).

> [!NOTE]
> Both options are for development only — any client can request a token. See [Token generation in production](#token-generation-in-production) before you ship.

## Token generation in production

In production, you will be responsible for developing a solution to [generate tokens for your users](https://docs.livekit.io/home/server/generating-tokens/) that integrates with your authentication system. Add an authentication layer to [`app/api/token/route.ts`](./app/api/token/route.ts), or point `tokenEndpoint` in [`app/page.tsx`](./app/page.tsx) at your own token server and drop the development token server.

## Project structure

This starter uses the [Agents UI](https://livekit.io/ui) components for core UI elements like media controls, audio visualizers, chat transcripts, and providing session data. Shadcn installs components into `components/` folder so you can customize them like any other local component.

```
agent-starter-react/
├── app/
│   ├── api/
├── components/
│   ├── agents-ui/     - Agents UI components
│   ├── app/           - App-specific components
│   ├── ui/            - Primitive shadcn/ui components
├── fonts/
├── hooks/
├── lib/
├── public/
└── package.json
```

Business logic lives within the `components/app` folder. It's here where the application's state and behavior is managed and the various Shadcn UI components are composed together.

| File                  | Description                                                                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `session-view.tsx`    | Initializes the application, and LiveKit session. Renders the view controller and session UI including chat transcript, media tiles, and control bar. |
| `view-controller.tsx` | Manages the transitions between the welcome and session views based on the LiveKit session state.                                                     |
| `welcome-view.tsx`    | Renders the welcome UI when the LiveKit session is not connected.                                                                                     |
| `chat-transcript.tsx` | Manages the chat transcript transitions.                                                                                                              |
| `tile-layout.tsx`     | Manages the layout and transition of media tiles in various application states.                                                                       |

### Component usage

Most Agents UI components require access to a LiveKit session object for access to values like agent state or audio tracks. A Session object can be created from a [TokenSource](/reference/client-sdk-js/variables/TokenSource.html), and provided by wrapping the component in an [AgentSessionProvider](/reference/components/shadcn/component/agent-session-provider).

See [`components/app/app.tsx`](./components/app/app.tsx) for an example of how this is done in this app.

### Customizing components

Agents UI components, like most Shadcn components, take as many primitive attributes as possible. For example, the [AgentControlBar](/reference/components/shadcn/component/agent-control-bar/page.mdoc) component extends `HTMLAttributes<HTMLDivElement>`, so you can pass any props that a div supports. This makes it easy to extend the component with your own styles or functionality.

You can edit any Agents UI component's source code in the `components/agents-ui` directory. For style changes, we recommend passing in tailwind classes to override the default styles. Take a look at the source code to get a sense of how to override a component's default styles.

### Updating components

To update the Agents UI components to the latest publication, run the following command:

```bash
pnpm shadcn:install
```

> [!NOTE]
> The CLI will ask before overwriting any modified files so you can avoid losing any customizations you might have made.

### Installing components

```bash
pnpm dlx shadcn@latest add @agents-ui/{component-name-a} @agents-ui/{component-name-b}
```

## Configuration

This starter is designed to be flexible so you can adapt it to your specific agent use case. Branding, feature toggles, and UI text are set directly in the components that use them — see [`app/layout.tsx`](./app/layout.tsx) for branding (logo, colors, page title/description) and [`components/app/view-controller.tsx`](./components/app/view-controller.tsx) for feature toggles and the audio visualizer. Video and screen share input follow the connected agent; override `isVideoInputSupported` in [`app/page.tsx`](./app/page.tsx) to force them on or off.

#### Audio visualizer presets

Set `audioVisualizerType` in [`components/app/view-controller.tsx`](./components/app/view-controller.tsx) to switch visualizer styles:

- `bar` (default): vertical bars with optional `audioVisualizerBarCount`
- `grid`: dot grid with `audioVisualizerGridRowCount` and `audioVisualizerGridColumnCount`
- `radial`: circular bars with `audioVisualizerRadialBarCount` and `audioVisualizerRadialRadius`
- `wave`: oscilloscope-style wave with `audioVisualizerWaveLineWidth`
- `aura`: shader-based aura with `audioVisualizerAuraColorShift`

Use `audioVisualizerColor` to set a shared accent color across all visualizer modes.

## Contributing

This template is open source and we welcome contributions! Please open a PR or issue through GitHub, and don't forget to join us in the [LiveKit Community Slack](https://livekit.io/join-slack)!
