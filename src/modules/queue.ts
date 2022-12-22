import axios, { AxiosInstance, AxiosResponse } from "axios";
import { headers } from "../common/requests";
import { wrapper } from "axios-cookiejar-support";
import { CookieJar } from "tough-cookie";
import { queueMonitorEmbed } from "../common/embed";
import { parseDomain, getFaviconUrl } from "../common/tools";

class ShopifyQueue {
	#domain: string;
	#icon: string;
	#queue: number = 0;
	#lastChecked: number = -1;
	#lastQueueToken: string;
	#client: AxiosInstance;

	private constructor(domain: string, client: AxiosInstance, queueToken: string) {
		this.#domain = domain;
		this.#icon = getFaviconUrl(domain);
		this.#lastQueueToken = queueToken;
		this.#client = client;
	}

	static initialize = async (input: string) => {
		const domain = parseDomain(input);

		let response: AxiosResponse = await axios.get(`https://${domain}/products.json`, { headers: headers });
		const placeholder: number = this.findAvailableVariant(response.data.products);
		if (placeholder === -1) {
			throw new Error("No available products found");
		}

		const client = wrapper(axios.create({ baseURL: `https://${domain}/`, jar: new CookieJar(), headers: headers }));
		await client.post("cart/add.js", { id: placeholder, quantity: 1 });

		// attempt to checkout and get initial queue token
		response = await client.get("checkout");
		const queueToken = response.config.jar?.toJSON().cookies.find((cookie) => cookie.key === "_checkout_queue_token")?.value;
		return new ShopifyQueue(domain, client, queueToken);
	};

	static findAvailableVariant = (products: any[]): number => {
		for (const product of products) {
			for (const variant of product.variants) {
				if (variant.available) {
					return variant.id;
				}
			}
		}
		return -1;
	};

	checkQueue = async (): Promise<number> => {
		this.#lastChecked = this.getTimestamp();
		const payload = {
			query: "\n{\npoll(token: $token) {\ntoken\npollAfter\nqueueEtaSeconds\nproductVariantAvailability {\nid\navailable\n}\n}\n}\n",
			variables: {
				token: this.#lastQueueToken,
			},
		};
		const response = await this.#client.post("queue/poll", payload);
		const data = response.data.data.poll;
        this.#queue = data.queueEtaSeconds;
        this.#lastQueueToken = data.token;
		return data.queueEtaSeconds;
	};

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
	};
}

class QueueDriver {
	#sites: ShopifyQueue[] = [];

	private constructor(sites: ShopifyQueue[]) {
		this.#sites = sites;
	}

	static initialize = async (inputs: string[]) => {
		const sites = await Promise.all(
			inputs.map(async (input) => {
				return await ShopifyQueue.initialize(input);
			})
		);
		return new QueueDriver(sites);
	};

	checkQueue = async () => {
		for await (const site of this.#sites) {
			const queue = await site.checkQueue();
            console.log(site.domain, "queue length", queue);
			queueMonitorEmbed(site);
		}
	};
}

(async () => {
	const driver = await QueueDriver.initialize(["https://kith.com", "https://dtlr.com/products/234234"]);
	await driver.checkQueue();
})();

export { QueueDriver, ShopifyQueue };
