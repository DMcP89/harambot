import discord


class ConfigModal(discord.ui.Modal, title="Configure Guild"):

    league_id = discord.ui.TextInput(
        label="Yahoo League ID", placeholder="Enter Yahoo League ID"
    )
    leauge_type = discord.ui.TextInput(
        label="Yahoo League Type",
        placeholder="Enter Yahoo League Type(nfl, nhl, nba, mlb)",
    )
    RIP_text = discord.ui.TextInput(
        label="RIP command text",
        placeholder="Enter text to use with $RIP command",
    )
    RIP_image_url = discord.ui.TextInput(
        label="RIP Image",
        placeholder="Enter image url to use with $RIP command",
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks for your feedback, {self.yahoo_auth_code.value}!",
            ephemeral=True,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:

        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
