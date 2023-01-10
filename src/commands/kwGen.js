import { AttachmentBuilder, SlashCommandBuilder } from 'discord.js';
import { genKWs } from '../modules/prefixer';

const data = new SlashCommandBuilder()
	.setName('kwgen')
	.setDescription('Add a prefix to a list of keywords')
	.addStringOption(option =>
		option.setName("prefix")
			.setDescription("Prefix you want to add")
			.setRequired(true))
	.addStringOption(option =>
		option.setName("keywords")
			.setDescription("List of keywords separated by spaces or commas")
			.setRequired(true));


export const command = {
	data: data,
	async execute(interaction) {
		const prefix = interaction.options.getString('prefix');
		const keywords = interaction.options.getString('keywords').split(/[ ,]+/);
		try {
			const prefixed = new AttachmentBuilder(Buffer.from(genKWs(prefix, keywords).join("\n"), 'utf-8'), { name: "prefixed.txt" });
			await interaction.reply({ files: [prefixed], ephemeral: true });
		} catch (error) {
			await interaction.reply("Error: " + error);
		}
	},
};