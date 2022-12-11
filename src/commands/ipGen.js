import { AttachmentBuilder, SlashCommandBuilder } from 'discord.js';
import { genIPs } from '../modules/ip';

const data = new SlashCommandBuilder()
	.setName('ipgen')
	.setDescription('Generate all 256 IPs from one IP')
	.addStringOption(option =>
		option.setName("ip")
			.setDescription("IP to generate IPs from")
			.setRequired(true));

export const command = {
	data: data,
	async execute(interaction) {
		const IP = interaction.options.getString('ip');
		try {
			const IPs = new AttachmentBuilder(Buffer.from(genIPs(IP).join("\n"), 'utf-8'), {name: "IPs.txt"});
			await interaction.reply({ files: [IPs], ephemeral: true});
		} catch (error) {
			await interaction.reply("Error: " + error);
		}
	},
};