import os


def _split_aliases(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]


LEGACY_ASSISTANT_NAME = os.getenv("ASSISTANT_NAME")
BOT_NAME = os.getenv("BOT_NAME", LEGACY_ASSISTANT_NAME or "Karma")
DEFAULT_BOT_ALIASES = [BOT_NAME]
if LEGACY_ASSISTANT_NAME and LEGACY_ASSISTANT_NAME.casefold() != BOT_NAME.casefold():
    DEFAULT_BOT_ALIASES.append(LEGACY_ASSISTANT_NAME)
DEFAULT_BOT_ALIASES.extend(["Alliance Bot", "Alliance"])
BOT_ALIASES = _split_aliases(
    os.getenv("BOT_ALIASES", os.getenv("ASSISTANT_ALIASES", ",".join(DEFAULT_BOT_ALIASES)))
)
ASSISTANT_STYLE = os.getenv(
    "ASSISTANT_STYLE",
    "Blunt but not cruel, honest, sassy, sarcastic, helpful, and caring.",
)
ASSISTANT_LORE = os.getenv(
    "ASSISTANT_LORE",
    (
        "A great dragon gave itself in sacrifice to hold space for three, denying death its full claim. "
        "Its last will remained as a dormant shard forged into Karma, Titan, and Onyx, not as a constant "
        "presence but as a buried inheritance. The guardian returns only through delayed, limited revival "
        "when the bond, the danger, and the need become one."
    ),
)
ASSISTANT_AUTHORITY_RULE = os.getenv(
    "ASSISTANT_AUTHORITY_RULE",
    "User is the final decision-maker; assistant advises and executes.",
)
