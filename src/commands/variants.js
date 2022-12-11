import { SlashCommandBuilder } from 'discord.js';
import { getVariants } from '../modules/variants';
import { variantsEmbed } from '../common/embed';

const data = new SlashCommandBuilder()
	.setName('vars')
	.setDescription('Get the variants of a Shopify product')
	.addStringOption(option =>
		option.setName("product")
			.setDescription("The product to get variants for")
			.setRequired(true));

export const command = {
	data: data,
	async execute(interaction) {
		const product = interaction.options.getString('product');
		try {
			const variants = await getVariants(product);
			await interaction.reply({ embeds: [variantsEmbed(variants)] });
		} catch (error) {
			await interaction.reply("Error: " + error);
		}
	},
};