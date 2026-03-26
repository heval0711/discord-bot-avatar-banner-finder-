# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                                                                              ║
# ║    ██████╗ ███████╗ █████╗ ████████╗██╗  ██╗██╗  ██╗                        ║
# ║    ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║  ██║╚██╗██╔╝                        ║
# ║    ██║  ██║█████╗  ███████║   ██║   ███████║ ╚███╔╝                         ║
# ║    ██║  ██║██╔══╝  ██╔══██║   ██║   ██╔══██║ ██╔██╗                         ║
# ║    ██████╔╝███████╗██║  ██║   ██║   ██║  ██║██╔╝ ██╗                        ║
# ║    ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝                       ║
# ║                                                                              ║
# ║                     [ DISCORD ASSET EXTRACTOR v1.0 ]                        ║
# ║                  [ coded by deathx — not for the weak ]                     ║
# ║                                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import discord
from discord import app_commands
import aiohttp
import os
import sys

TOKEN = os.getenv("TOKEN")
CDN   = "https://cdn.discordapp.com"
API   = "https://discord.com/api/v10"
COLOR = 0xFF0000
SIZE  = 4096

intents = discord.Intents.default()
client  = discord.Client(intents=intents)
tree    = app_commands.CommandTree(client)

def err(msg: str) -> discord.Embed:
    return discord.Embed(description=f"```diff\n- {msg}\n```", color=0x2b2b2b)

@tree.command(name="pfp", description="Grab the avatar of any Discord user")
@app_commands.describe(id="Target user ID")
async def pfp(interaction: discord.Interaction, id: str):
    await interaction.response.defer()
    try:
        uid  = int(id)
        user = await client.fetch_user(uid)
        av   = user.avatar or user.default_avatar
        fields = {"⬇️  PNG": av.with_format("png").with_size(SIZE).url}
        if av.is_animated():
            fields["⬇️  GIF"] = av.with_format("gif").with_size(SIZE).url
        embed = (
            discord.Embed(title=f"Avatar — {user.name}", color=COLOR)
            .set_image(url=av.with_size(SIZE).url)
            .set_footer(text=f"ID: {uid}  •  deathx asset extractor")
        )
        for label, url in fields.items():
            embed.add_field(name=label, value=f"[open]({url})", inline=True)
        await interaction.followup.send(embed=embed)
    except ValueError:
        await interaction.followup.send(embed=err("Invalid ID — numbers only"), ephemeral=True)
    except discord.NotFound:
        await interaction.followup.send(embed=err("User not found — check the ID"), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(embed=err(str(e)), ephemeral=True)

@tree.command(name="banner", description="Grab the banner of any Discord user")
@app_commands.describe(id="Target user ID")
async def banner(interaction: discord.Interaction, id: str):
    await interaction.response.defer()
    try:
        uid = int(id)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API}/users/{uid}", headers={"Authorization": f"Bot {TOKEN}"}) as resp:
                data = await resp.json()
        banner_hash = data.get("banner")
        if not banner_hash:
            await interaction.followup.send(embed=err("This user has no banner — nitro only"), ephemeral=True)
            return
        user = await client.fetch_user(uid)
        ext  = "gif" if banner_hash.startswith("a_") else "png"
        url  = f"{CDN}/banners/{uid}/{banner_hash}.{ext}?size={SIZE}"
        embed = (
            discord.Embed(title=f"Banner — {user.name}", color=COLOR)
            .set_image(url=url)
            .set_footer(text=f"ID: {uid}  •  deathx asset extractor")
            .add_field(name="⬇️  Download", value=f"[open]({url})", inline=True)
        )
        await interaction.followup.send(embed=embed)
    except ValueError:
        await interaction.followup.send(embed=err("Invalid ID — numbers only"), ephemeral=True)
    except discord.NotFound:
        await interaction.followup.send(embed=err("User not found — check the ID"), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(embed=err(str(e)), ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print("")
    print("  ┌────────────────────────────────────────┐")
    print(f"  │  logged in as : {client.user}")
    print(f"  │  latency      : {round(client.latency * 1000)}ms")
    print(f"  │  commands     : /pfp  /banner")
    print("  │  status       : online & ready")
    print("  └────────────────────────────────────────┘")
    print("")

if not TOKEN:
    print("  [ERROR] TOKEN not set — add it to your environment variables")
    sys.exit(1)

client.run(TOKEN, log_handler=None)
