import { SlashCommandBuilder } from 'discord.js';

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
		console.log(interaction.options);
	},
};