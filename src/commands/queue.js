import { ActionRowBuilder, ButtonBuilder, ButtonStyle, SlashCommandBuilder } from 'discord.js';
import { QueueDriver } from '../modules/queue';
import { queueMonitorEmbed } from '../common/embed';

let running = false;
// timeout to stop monitoring queue after 30 min if not stopped manually
let timeout;
// interval to check queue every NUM_SEC seconds
let interval;
// controller for site queues
let driver;
// channel to send messages in
let channel;
let messages = {};
const NUM_SEC = 5;
const STOP_TIMEOUT = 30 * 60;

export const stopQueueDriver = async () => {
	if (running) {
		running = false;
		clearInterval(interval);
		clearTimeout(timeout);
		for (const site in messages) {
			await messages[site].delete();
		}
	}
};

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
			.setRequired(false));

export const command = {
	data: data,
	async execute(interaction) {
		if (running) {
			const sites = "```\n" + driver.sites.map(site => site.domain).join("\n") + "\n```";
			await interaction.reply({ content: `Already monitoring queue for ${sites}`, ephemeral: true });
			return;
		}

		const button = new ActionRowBuilder().addComponents(
			new ButtonBuilder()
				.setCustomId('stop-queue')
				.setLabel('Stop')
				.setStyle(ButtonStyle.Danger)
		)
		await interaction.reply({ content: `Monitoring queue. Stopping at <t:${Math.floor(Date.now() / 1000) + STOP_TIMEOUT}:T>`, components: [button]});
		channel = interaction.channel;
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

		driver = await QueueDriver.initialize(inputs);
		running = true;
		let sites = driver.sites;
		for await (const site of sites) {
			const ref = await channel.send({ embeds: [queueMonitorEmbed(site)] });
			messages[site.domain] = ref;
		}

		interval = setInterval(async () => {
			sites = await driver.getSiteQueues();
			for await (const site of sites) {
				await messages[site.domain].edit({ embeds: [queueMonitorEmbed(site)] });
			}
		}, NUM_SEC * 1000)

		// stop after 30 minutes if it hasn't been stopped already
		timeout = setTimeout(async () => {
			await channel.send("Done monitoring queue.");
			await stopQueueDriver();
		}, STOP_TIMEOUT * 1000)
	},
};