import { ActionRowBuilder, ButtonBuilder, ButtonStyle, SlashCommandBuilder } from 'discord.js';
import { QueueDriver } from '../modules/queue';

let running = false;

const data = new SlashCommandBuilder()
	.setName('queue')
	.setDescription('Monitor Shopify queue')
	.addStringOption(option =>
		option.setName("site1")
			.setDescription("site to track queue for")
			.setRequired(true))
	.addStringOption(option =>
		option.setName("site2")
			.setDescription("site to track queue for")
			.setRequired(false))
	.addStringOption(option =>
		option.setName("site3")
			.setDescription("site to track queue for")
			.setRequired(false))
	.addStringOption(option =>
		option.setName("site4")
			.setDescription("site to track queue for")
			.setRequired(false))
	.addStringOption(option =>
		option.setName("site5")
			.setDescription("site to track queue for")
			.setRequired(false))

export const command = {
	data: data,
	async execute(interaction) {
		await interaction.reply("not implemented yet");
		return;
		let interval;
		if (running) {
			const row = new ActionRowBuilder().addComponents(
				new ButtonBuilder()
					.setCustomId('stop')
					.setLabel('Stop')
					.setStyle(ButtonStyle.Danger)
			)
			await interaction.reply({ content: "Already monitoring queue. Do you want to stop?", components: [row] });
			return;
		}
		// QueueDriver.initialize(["https://kith.com", "https://dtlr.com/products/234234"]);
		await interaction.reply("Monitoring queue...");
		running = true;
		const messages = [];
		for (let i = 1; i <= 2; i++) {
			const ref = await interaction.channel.send("Monitoring " + interaction.options.getString("site" + i));
			messages.push(ref);
		}
		let counter = 1
		interval = setInterval(async () => {
			for await (const ref of messages) {
				await ref.edit("Monitoring " + counter);
				counter += 1;
			}
		}, 5000)

		// stop after 30 minutes if it hasn't been stopped already
		setTimeout(() => {
			clearInterval(interval);
			interaction.channel.send("Done monitoring queue.");
		}, 30 * 60 * 1000)
	},
};