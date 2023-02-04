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
			.setRequired(true))
    .addStringOption(option =>
        option.setName("find_what")
            .setDescription("Keyword or character that you want to replace")
            .setRequired(false))
    .addStringOption(option =>
        option.setName("replace_with")
            .setDescription("What you want to replace with")
            .setRequired(false));


export const command = {
	data: data,
	async execute(interaction) {
		const prefix = interaction.options.getString('prefix');
		let keywords = interaction.options.getString('keywords').split(/[ ,]+/);
        const find = interaction.options.getString('find_what');
        const replace = interaction.options.getString('replace_with');
        if (find !== null && replace === null) {
            await interaction.reply("Error: You must provide a replacement");
            return;
        }
		try {
            if (find !== null && replace !== null) {
                // replace() only replaces the first match by default
                // adding the "g" flag makes it replace all matches
                const regExp = new RegExp(find, "g");
                keywords = keywords.map(keyword => keyword.replace(regExp, replace));
            }
			const prefixed = new AttachmentBuilder(Buffer.from(genKWs(prefix, keywords).join("\n"), 'utf-8'), { name: "prefixed.txt" });
			await interaction.reply({ files: [prefixed], ephemeral: true });
		} catch (error) {
			await interaction.reply("Error: " + error);
		}
	},
};