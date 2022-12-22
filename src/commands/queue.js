import { ActionRowBuilder, ButtonBuilder, ButtonStyle, SlashCommandBuilder } from 'discord.js';
import { QueueDriver } from '../modules/queue';
import { queueMonitorEmbed } from '../common/embed';

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
		// await interaction.reply("not implemented yet");
		// return;
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

		await interaction.reply("Monitoring queue...");

		const inputs = [];
		if (interaction.options.getString('site1') !== null) {
			inputs.push(interaction.options.getString('site1'));
		}
		if (interaction.options.getString('site2') !== null) {
			inputs.push(interaction.options.getString('site2'));
		}
		if (interaction.options.getString('site3') !== null) {
			inputs.push(interaction.options.getString('site3'));
		}
		if (interaction.options.getString('site4') !== null) {
			inputs.push(interaction.options.getString('site4'));
		}
		if (interaction.options.getString('site5') !== null) {
			inputs.push(interaction.options.getString('site5'));
		}

		const driver = await QueueDriver.initialize(inputs);
		running = true;
		let sites = driver.sites;
		const messages = {};
		for await (const site of sites) {
			const ref = await interaction.channel.send({ embeds: [queueMonitorEmbed(site)] });
			messages[site.domain] = ref;
		}

		interval = setInterval(async () => {
			sites = await driver.getSiteQueues();
			for await (const site of sites) {
				await messages[site.domain].edit({ embeds: [queueMonitorEmbed(site)] });
			}
		}, 5 * 1000)

		// stop after 30 minutes if it hasn't been stopped already
		setTimeout(() => {
			clearInterval(interval);
			interaction.channel.send("Done monitoring queue.");
		}, 30 * 60 * 1000)
	},
};