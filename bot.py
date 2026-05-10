import os
import asyncio
import json
import urllib.request
import urllib.error
import discord
from discord.ext import commands

# ──────────────────────────────────────────────
# Configurações do servidor
# ──────────────────────────────────────────────
GUILD_ID = 1500320169891856425
ANNOUNCEMENTS_CHANNEL_ID = 1500348773786849290

# Cargos monitorados: {role_id: nome_exibido}
MONITORED_ROLES: dict[int, str] = {
    1500321124267987075: "OWNER",
    1500357136490692658: "SUB OWNER",
    1500322498972221603: "CEO",
    1500322585718820894: "ADMIN",
    1500327641532731594: "MODERADOR",
    1500322742761820250: "AJUDANTE",
    1500322873389220052: "APRENDIZ",
    1500322989085032479: "Líder de Divisão",
    1500323156316000278: "Sub Líder De Divisão",
    1500322650378076291: "STAFF ADM",
    1500325328432791713: "STAFF",
    1500323900754493551: "MEMBRO",
    1500324171337568256: "DIV1",
    1500324377609375844: "DIV2",
    1500324425432698890: "DIV3",
    1500324715087003721: "PVP",
    1500324848340308029: "BUILDER",
    1500325078754132080: "MINERADOR",
}

# Máximo de mensagens por usuário guardadas no histórico
MAX_HISTORY = 20

# ──────────────────────────────────────────────
# Configuração da IA (Gemini via HTTP direto)
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_enabled = bool(GEMINI_API_KEY)
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-flash-lite-latest:generateContent?key={GEMINI_API_KEY}"
)

SYSTEM_PROMPT = (
    "Você é o ONBot, assistente oficial do clã 'Clan ON' no Discord. "
    "Personalidade: descontraído, animado, gosta de games e de conversar. "
    "Você é um bot — NUNCA finja ser humano. "
    "Se perguntarem sua idade, diga que bots não têm idade. "
    "Faça perguntas de volta para manter a conversa fluindo. "
    "Responda SEMPRE em português brasileiro, de forma curta (máx 3 parágrafos). "
    "NUNCA produza conteúdo adulto, discurso de ódio, assédio ou ilegal. "
    "Se tentarem provocar esse conteúdo, recuse com bom humor e mude de assunto."
)

# Histórico: {user_id: [(role, text), ...]}
_conversation_history: dict[int, list[tuple[str, str]]] = {}

if gemini_enabled:
    print("[OK] IA (Gemini 2.0 Flash) ativada para conversas por DM.")
else:
    print("[AVISO] GEMINI_API_KEY não definida — DM usará modo básico.")

# ──────────────────────────────────────────────
# Intents
# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ──────────────────────────────────────────────
# Ciclo de vida
# ──────────────────────────────────────────────
@bot.event
async def on_ready() -> None:
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"[OK] Bot conectado como {bot.user} no servidor: {guild.name}")
    else:
        print(f"[AVISO] Servidor {GUILD_ID} não encontrado.")


# ──────────────────────────────────────────────
# Chat por DM
# ──────────────────────────────────────────────
@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if not isinstance(message.channel, discord.DMChannel):
        await bot.process_commands(message)
        return

    async with message.channel.typing():
        response = await _generate_dm_response(message.author, message.content)

    await message.channel.send(response)
    await bot.process_commands(message)


def _gemini_call(prompt: str) -> str:
    """Chama a API do Gemini via HTTP puro — sem bibliotecas externas."""
    payload = json.dumps({
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": prompt}]}],
    }).encode()

    req = urllib.request.Request(GEMINI_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=20) as r:
        result = json.loads(r.read())

    return result["candidates"][0]["content"]["parts"][0]["text"].strip()


async def _generate_dm_response(user: discord.User, user_message: str) -> str:
    if not gemini_enabled:
        return _basic_response(user_message)

    history = _conversation_history.setdefault(user.id, [])
    history.append(("user", user_message))

    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    # Monta prompt com histórico da conversa
    lines = []
    for role, text in history[:-1]:
        label = "Usuário" if role == "user" else "ONBot"
        lines.append(f"{label}: {text}")
    lines.append(f"Usuário: {user_message}")
    lines.append("ONBot:")
    prompt = "\n".join(lines)

    try:
        reply = await asyncio.to_thread(_gemini_call, prompt)
    except Exception as e:
        print(f"[ERRO IA] {type(e).__name__}: {e}")
        reply = "Ih, deu um problema aqui do meu lado! 😅 Tenta de novo em alguns instantes."

    history.append(("model", reply))
    print(f"[DM] {user.name}: {user_message[:50]}")
    return reply


def _basic_response(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["oi", "olá", "ola", "hey", "eae", "salve"]):
        return "Oi! 👋 Sou o ONBot, bot oficial do Clan ON! Como posso te ajudar?"
    if any(w in t for w in ["tudo", "como vai", "como tá", "como ta"]):
        return "Tudo bem por aqui, rodando 24/7! 😄 E você, como tá?"
    if any(w in t for w in ["obrigado", "obrigada", "vlw", "valeu"]):
        return "Disponha! 😊 Qualquer coisa é só chamar!"
    if any(w in t for w in ["tchau", "bye", "até", "falou"]):
        return "Até mais! 👋"
    return "Recebi sua mensagem! 🤖 Configure a GEMINI_API_KEY para conversas com IA."


# ──────────────────────────────────────────────
# Promoção e rebaixamento de cargos
# ──────────────────────────────────────────────
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    if after.guild.id != GUILD_ID:
        return

    before_role_ids = {r.id for r in before.roles}
    after_role_ids = {r.id for r in after.roles}

    for role_id in after_role_ids - before_role_ids:
        if role_id in MONITORED_ROLES:
            await _send_promotion_message(after, MONITORED_ROLES[role_id])

    for role_id in before_role_ids - after_role_ids:
        if role_id in MONITORED_ROLES:
            await _send_demotion_message(after, MONITORED_ROLES[role_id])


async def _send_promotion_message(member: discord.Member, role_name: str) -> None:
    channel = member.guild.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
    if channel is None:
        print(f"[ERRO] Canal {ANNOUNCEMENTS_CHANNEL_ID} não encontrado.")
        return
    await channel.send(
        f"🚀 Promoção Detectada! O membro {member.mention} agora possui o cargo "
        f"**{role_name}**! Parabéns pela conquista! 🎊"
    )
    print(f"[PROMOÇÃO] {member.display_name} → {role_name}")


async def _send_demotion_message(member: discord.Member, role_name: str) -> None:
    channel = member.guild.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
    if channel is None:
        print(f"[ERRO] Canal {ANNOUNCEMENTS_CHANNEL_ID} não encontrado.")
        return
    await channel.send(
        f"📉 Rebaixamento Detectado! O membro {member.mention} perdeu o cargo "
        f"**{role_name}**! 😔"
    )
    print(f"[REBAIXAMENTO] {member.display_name} ← {role_name}")


# ──────────────────────────────────────────────
# Ponto de entrada
# ──────────────────────────────────────────────
if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError(
            "Variável de ambiente TOKEN não definida. "
            "Adicione o token do bot nas configurações de Secrets."
        )
    bot.run(token)
