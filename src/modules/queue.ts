import axios, { AxiosInstance, AxiosResponse } from "axios";
import { headers } from "../common/requests";
import { wrapper } from 'axios-cookiejar-support';
import { CookieJar } from 'tough-cookie';

class ShopifyMonitor {
    #domain: string;
    #client: AxiosInstance;
    #placeholder: number;

    private constructor(domain: string, placeholder: number) {
        this.#domain = domain;
        this.#client = wrapper(axios.create({ baseURL: `https://${domain}/`, jar: new CookieJar(), headers: headers }));
        this.#placeholder = 0;
        console.log(`Initialized ${domain} with placeholder ${placeholder}`);
    }

    static initialize = async (input: string) => {
        const domain = this.parseDomain(input);

        const url: string = `https://${domain}/products.json`;
        const response: AxiosResponse = await axios.get(url, { headers: headers });
        const placeholder: number = this.findAvailableVariant(response.data.products);

        return new ShopifyMonitor(domain, placeholder);
    }

    static findAvailableVariant = (products: any[]): number => {
        for (const product of products) {
            for (const variant of product.variants) {
                if (variant.available) {
                    return variant.id;
                }
            }
        }
        return -1;
    }

    static parseDomain = (input: string): string => {
        if (!input.includes(".")) {
            return input.toLowerCase();
        }

        const domain: RegExpMatchArray | null = input.match(/\w+(?:\.\w+)+/);
        if (domain === null) {
            throw new Error("Cannot parse domain");
        }
        return domain[0].toLowerCase();
    }
}

class QueueDriver {
    static #domains: ShopifyMonitor[] = [];

    static initialize = async (inputs: string[]) => {
        for await (const input of inputs) {
            this.#domains.push(await ShopifyMonitor.initialize(input));
        }
    }
}

const queue = QueueDriver.initialize(["https://kith.com", "https://dtlr.com/products/234234"]);

export default QueueDriver;