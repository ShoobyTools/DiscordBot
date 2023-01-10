const genKWs = (prefix: string, keywords: string[]): string[] => {
	return keywords.map((keyword) => `${prefix}${keyword}`);
};

export { genKWs };
