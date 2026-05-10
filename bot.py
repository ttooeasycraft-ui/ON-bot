import os
import asyncio
import discord
from discord.ext import commands
import google.generativeai as genai

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

# Máximo de mensagens por usuário guardadas no histórico de conversa
MAX_HISTORY = 20

# ──────────────────────────────────────────────
# Configuração da IA (Gemini)
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_enabled = bool(GEMINI_API_KEY)

if gemini_enabled:
    genai.configure(api_key=GEMINI_API_KEY)
    _ai_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "Você é o ONBot, assistente oficial do clã 'Clan ON' no Discord. "
            "Sua personalidade: descontraído, animado, gosta de games e de conversar. "
            "Você é um bot — nunca finja ser humano nem diga que é humano. "
            "Se alguém perguntar sua idade, diga que bots não têm idade mas que foi criado recentemente. "
            "Faça perguntas de volta para manter a conversa fluindo — pergunte como a pessoa tá, "
            "qual jogo ela joga, como tá o clã, etc. "
            "Responda sempre em português brasileiro, de forma curta e natural (máx 3 parágrafos). "
            "NUNCA produza conteúdo que viole os Termos de Serviço do Discord: "
            "sem conteúdo adulto, sem discurso de ódio, sem assédio, sem informações ilegais, "
            "sem incentivo a violência. Se o usuário tentar provocar esse tipo de conteúdo, "
            "recuse com bom humor e mude de assunto."
        ),
    )
    # Histórico de conversa por usuário: {user_id: [{"role": ..., "parts": [...]}]}
    _conversation_history: dict[int, list[dict]] = {}
    print("[OK] IA (Gemini) ativada para conversas por DM.")
else:
    print("[AVISO] GEMINI_API_KEY não definida — respostas por DM usarão modo básico.")

# ──────────────────────────────────────────────
# Intents
# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ──────────────────────────────────────────────
# Eventos de ciclo de vida
# ──────────────────────────────────────────────
@bot.event
async def on_ready() -> None:
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"[OK] Bot conectado como {bot.user} no servidor: {guild.name}")
    else:
        print(
            f"[AVISO] Bot conectado como {bot.user}, "
            f"mas o servidor {GUILD_ID} não foi encontrado."
        )


# ──────────────────────────────────────────────
# Chat por DM com IA
# ──────────────────────────────────────────────
@bot.event
async def on_message(message: discord.Message) -> None:
    # Ignora mensagens do próprio bot
    if message.author.bot:
        return

    # Só age em DMs (mensagem direta, não em servidores)
    if not isinstance(message.channel, discord.DMChannel):
        await bot.process_commands(message)
        return

    async with message.channel.typing():
        response = await _generate_dm_response(message.author, message.content)

    await message.channel.send(response)

    # Permite que comandos ! também funcionem em DMs
    await bot.process_commands(message)


async def _generate_dm_response(user: discord.User, user_message: str) -> str:
    """Gera resposta para DM usando Gemini ou modo básico."""
    if not gemini_enabled:
        return _basic_response(user_message)

    history = _conversation_history.setdefault(user.id, [])

    # Adiciona mensagem do usuário ao histórico (formato correto do Gemini)
    history.append({"role": "user", "parts": [{"text": user_message}]})

    # Mantém histórico limitado (últimas MAX_HISTORY mensagens)
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    try:
        def _call_gemini() -> str:
            chat = _ai_model.start_chat(history=history[:-1])
            return chat.send_message(user_message).text.strip()

        reply = await asyncio.to_thread(_call_gemini)
    except Exception as e:
        import traceback
        print(f"[ERRO IA] {e}")
        traceback.print_exc()
        reply = (
            "Ih, deu um problema aqui do meu lado! 😅 "
            "Tenta de novo em alguns instantes."
        )

    # Adiciona resposta do bot ao histórico (formato correto do Gemini)
    history.append({"role": "model", "parts": [{"text": reply}]})
    print(f"[DM] {user.name}: {user_message[:50]} → resposta gerada")
    return reply


def _basic_response(text: str) -> str:
    """Respostas simples para quando a IA não está configurada."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["oi", "olá", "ola", "hey", "eae", "salve"]):
        return (
            "Oi! 👋 Sou o ONBot, bot oficial do Clan ON! "
            "Como posso te ajudar hoje?"
        )
    if any(w in text_lower for w in ["tudo", "como vai", "como tá", "como ta"]):
        return "Tudo bem por aqui, rodando 24/7! 😄 E você, como tá?"
    if any(w in text_lower for w in ["obrigado", "obrigada", "vlw", "valeu"]):
        return "Disponha! 😊 Qualquer coisa é só chamar!"
    if any(w in text_lower for w in ["tchau", "bye", "até", "falou"]):
        return "Até mais! 👋 Qualquer coisa é só chamar!"
    return (
        "Recebi sua mensagem! 🤖 Para ter conversas completas comigo, "
        "peça para o admin configurar a GEMINI_API_KEY."
    )


# ──────────────────────────────────────────────
# Detecção de promoção e rebaixamento de cargos
# ──────────────────────────────────────────────
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    # Ignora eventos de servidores diferentes do configurado
    if after.guild.id != GUILD_ID:
        return

    before_role_ids = {r.id for r in before.roles}
    after_role_ids = {r.id for r in after.roles}

    newly_added_ids = after_role_ids - before_role_ids
    newly_removed_ids = before_role_ids - after_role_ids

    for role_id in newly_added_ids:
        if role_id not in MONITORED_ROLES:
            continue
        await _send_promotion_message(after, MONITORED_ROLES[role_id])

    for role_id in newly_removed_ids:
        if role_id not in MONITORED_ROLES:
            continue
        await _send_demotion_message(after, MONITORED_ROLES[role_id])


async def _send_promotion_message(member: discord.Member, role_name: str) -> None:
    """Envia a mensagem de promoção no canal de avisos."""
    channel = member.guild.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
    if channel is None:
        print(f"[ERRO] Canal de avisos {ANNOUNCEMENTS_CHANNEL_ID} não encontrado.")
        return

    message = (
        f"🚀 Promoção Detectada! O membro {member.mention} agora possui o cargo "
        f"**{role_name}**! Parabéns pela conquista! 🎊"
    )
    await channel.send(message)
    print(f"[PROMOÇÃO] {member.display_name} → {role_name}")


async def _send_demotion_message(member: discord.Member, role_name: str) -> None:
    """Envia a mensagem de rebaixamento no canal de avisos."""
    channel = member.guild.get_channel(ANNOUNCEMENTS_CHANNEL_ID)
    if channel is None:
        print(f"[ERRO] Canal de avisos {ANNOUNCEMENTS_CHANNEL_ID} não encontrado.")
        return

    message = (
        f"📉 Rebaixamento Detectado! O membro {member.mention} perdeu o cargo "
        f"**{role_name}**! 😔"
    )
    await channel.send(message)
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
