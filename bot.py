import os
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

# ──────────────────────────────────────────────
# Intents
# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.guilds = True

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
            f"[AVISO] Bot conectado como {bot.user}, mas o servidor {GUILD_ID} não foi encontrado."
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
        print(
            f"[ERRO] Canal de avisos {ANNOUNCEMENTS_CHANNEL_ID} não encontrado no servidor."
        )
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
        print(
            f"[ERRO] Canal de avisos {ANNOUNCEMENTS_CHANNEL_ID} não encontrado no servidor."
        )
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
