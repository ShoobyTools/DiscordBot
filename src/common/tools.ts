const parseDomain = (input: string): string => {
    if (!input.includes(".")) {
        return input.toLowerCase();
    }

    const domain: RegExpMatchArray | null = input.match(/\w+(?:\.\w+)+/);
    if (domain === null) {
        throw new Error("Cannot parse domain");
    }
    return domain[0].toLowerCase();
}

const getFaviconUrl = (domain: string): string => {
    return `https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://${domain}&size=64`;
}

export { parseDomain, getFaviconUrl };