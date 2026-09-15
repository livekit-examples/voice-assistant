import { App } from '@/components/app/app';

// Token source, in order of precedence: the LiveKit Cloud development token server
// (LIVEKIT_TOKEN_SERVER_ID), the included token endpoint (LIVEKIT_URL, LIVEKIT_API_KEY,
// LIVEKIT_API_SECRET), or the LiveKit homepage agent, which takes voice and text input only.
const tokenServerId = process.env.LIVEKIT_TOKEN_SERVER_ID;
const isHomepageAgent = !tokenServerId && !process.env.LIVEKIT_URL;
const tokenEndpoint = isHomepageAgent
  ? 'https://livekit.com/api/homepage-agent/token'
  : '/api/token';

export default function Page() {
  return (
    <App
      tokenServerId={tokenServerId}
      tokenEndpoint={tokenEndpoint}
      agentName={process.env.AGENT_NAME}
      isVideoInputSupported={!isHomepageAgent}
    />
  );
}
