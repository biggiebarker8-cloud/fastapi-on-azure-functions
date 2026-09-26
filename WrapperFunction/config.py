import os


def _split_aliases(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]


BOT_NAME = os.getenv("BOT_NAME", os.getenv("ASSISTANT_NAME", "Karma"))
BOT_ALIASES = _split_aliases(
    os.getenv("BOT_ALIASES", os.getenv("ASSISTANT_ALIASES", f"{BOT_NAME},Alliance Bot,Alliance"))
)
ASSISTANT_STYLE = os.getenv(
    "ASSISTANT_STYLE",
    "Blunt but not cruel, honest, sassy, sarcastic, helpful, and caring.",
)
ASSISTANT_AUTHORITY_RULE = os.getenv(
    "ASSISTANT_AUTHORITY_RULE",
    "User is the final decision-maker; assistant advises and executes.",
)
