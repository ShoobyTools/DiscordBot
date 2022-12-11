const parseProxy = (proxy: string): string[] => {
    const prefix: RegExpMatchArray | null = proxy.match(/(?:\d+\.){3}/);
    const suffix: RegExpMatchArray | null = proxy.match(/(?::.+){2,3}/);

    if (prefix === null) {
        throw new Error("Improperly formatted IP address (prefix)");
    }
    if (suffix === null) {
        throw new Error("Improperly formatted IP address (suffix)");
    }

    const prefixString: string = prefix[0];
    const suffixString: string = suffix[0];
    const ipRange: string[] = [];
    for (let i = 0; i < 256; i++) {
        ipRange.push(`${prefixString}${i}${suffixString}`);
    }

    return ipRange;
}

export {parseProxy};