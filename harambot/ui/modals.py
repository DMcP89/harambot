import discord


class ConfigModal(discord.ui.Modal, title="Configure Guild"):

    name = discord.ui.TextInput(
        label="Name",
        placeholder="Your name here...",
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks for your feedback, {self.name.value}!", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:

        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
