const parseDomain = (input: string): string => {
	if (!input.includes(".")) {
		return input.toLowerCase() + ".com";
	}

	const domain = new URL(input);
	return domain.hostname.replace("www.", "").toLowerCase();
};

const getFaviconUrl = (domain: string): string => {
	return `https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://${domain}&size=64`;
};

export { parseDomain, getFaviconUrl };
