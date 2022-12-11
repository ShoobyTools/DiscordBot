import axios, { AxiosInstance, AxiosResponse } from "axios";
import { headers } from "../common/requests";
import { wrapper } from 'axios-cookiejar-support';
import { CookieJar } from 'tough-cookie';
import { queueMonitorEmbed } from "../common/embed";

class ShopifyQueue {
    #domain: string;
    #icon: string;
    #queue: number = 0;
    #lastChecked: number = -1;
    #client: AxiosInstance;
    #placeholder: number;

    private constructor(domain: string, placeholder: number) {
        this.#domain = domain;
        this.#icon = `https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://${domain}&size=64`;
        this.#client = wrapper(axios.create({ baseURL: `https://${domain}/`, jar: new CookieJar(), headers: headers }));
        this.#placeholder = placeholder;
        console.log(`Initialized ${domain} with placeholder ${placeholder}`);
    }

    static initialize = async (input: string) => {
        const domain = this.parseDomain(input);

        const url: string = `https://${domain}/products.json`;
        const response: AxiosResponse = await axios.get(url, { headers: headers });
        const placeholder: number = this.findAvailableVariant(response.data.products);

        return new ShopifyQueue(domain, placeholder);
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

    checkQueue = async (): Promise<number> => {
        this.#lastChecked = this.getTimestamp();
        const url: string = `https://${this.#domain}/cart/add.js`;
        const response: AxiosResponse = await this.#client.post(url, { id: this.#placeholder, quantity: 1 });
        console.log(response.status);
        return response.status;
    }

    get domain(): string {
        return this.#domain;
    }

    get icon(): string {
        return this.#icon;
    }

    get queue(): number {
        return this.#queue;
    }

    get lastChecked(): number {
        return this.#lastChecked;
    }

    get expectedPassTime(): number {
        return this.#lastChecked + this.#queue;
    }

    // returns UNIX timestamp in seconds
    private getTimestamp = (): number => {
        return Date.now() / 1000;
    }
}

class QueueDriver {
    static #sites: ShopifyQueue[] = [];

    static initialize = async (inputs: string[]) => {
        for await (const input of inputs) {
            this.#sites.push(await ShopifyQueue.initialize(input));
        }
    }

    static checkQueue = async () => {
        for await (const site of this.#sites) {
            await site.checkQueue();
            queueMonitorEmbed(site)
        }
    }
}

// const queue = QueueDriver.initialize(["https://kith.com", "https://dtlr.com/products/234234"]);

export { QueueDriver, ShopifyQueue };