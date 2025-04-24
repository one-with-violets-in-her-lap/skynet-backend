import g4f.Provider

ALL_G4F_PROVIDERS = [
    g4f.Provider.AllenAI,
    g4f.Provider.ARTA,
    g4f.Provider.Blackbox,
    g4f.Provider.ChatGLM,
    g4f.Provider.ChatGpt,
    g4f.Provider.ChatGptEs,
    g4f.Provider.Cloudflare,
    g4f.Provider.Copilot,
    g4f.Provider.DDG,
    g4f.Provider.DeepInfraChat,
    g4f.Provider.Dynaspark,
    g4f.Provider.Free2GPT,
    g4f.Provider.FreeGpt,
    g4f.Provider.GizAI,
    g4f.Provider.Glider,
    g4f.Provider.Goabror,
    g4f.Provider.ImageLabs,
    g4f.Provider.Jmuz,
    g4f.Provider.LambdaChat,
    g4f.Provider.Liaobots,
    g4f.Provider.OIVSCode,
    g4f.Provider.PerplexityLabs,
    g4f.Provider.Pi,
    g4f.Provider.Pizzagpt,
    g4f.Provider.PollinationsAI,
    g4f.Provider.PollinationsImage,
    g4f.Provider.TeachAnything,
    g4f.Provider.TypeGPT,
    g4f.Provider.You,
    g4f.Provider.Websim,
    g4f.Provider.Yqcloud,
    g4f.Provider.HailuoAI,
    g4f.Provider.MiniMax,
    g4f.Provider.HuggingFace,
    g4f.Provider.HuggingChat,
    g4f.Provider.HuggingFaceAPI,
    g4f.Provider.HuggingFaceInference,
    g4f.Provider.HuggingFaceMedia,
    g4f.Provider.OpenaiTemplate,
    g4f.Provider.BackendApi,
]


class RetryProviderWithIgnoring(g4f.Provider.RetryProvider):
    def __init__(self, ignored_providers: list[type[g4f.Provider.BaseProvider]]):
        super().__init__(
            providers=[
                provider
                for provider in ALL_G4F_PROVIDERS
                if provider not in ignored_providers
            ]
        )
