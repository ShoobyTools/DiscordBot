import axios, { AxiosInstance } from "axios";
import { headers } from "../common/requests";
import { wrapper } from "axios-cookiejar-support";
import { CookieJar } from "tough-cookie";
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

		let response;
		try {
			response = await axios.get(`https://${domain}/products.json`, { headers: headers });
		} catch (error) {
			throw new Error("Axios error on getting products for " + domain);
		}

		if (response.status !== 200) {
			throw new Error("Unable to get products for " + domain);
		}

		const placeholder = this.findAvailableVariant(response.data.products);
		if (placeholder === null) {
			throw new Error("No available products found for " + domain);
		}

		const client = wrapper(axios.create({ baseURL: `https://${domain}/`, jar: new CookieJar(), headers: headers }));
		try {
			response = await client.post("cart/add.js", { id: placeholder, quantity: 1 });
		} catch (error) {
			throw new Error("Axios error on adding to cart for " + domain);
		}

		if (response.status !== 200) {
			throw new Error("Unable to add placeholder product to cart for " + domain);
		}

		// attempt to checkout and get initial queue token
		try {
			response = await client.get("checkout");
		} catch (error) {
			throw new Error("Axios error on attempting checkout for " + domain);
		}

		let queueToken: string;
		if (response.status !== 200) {
			throw new Error("Unable to attempt checkout for " + domain);
		}
		if (response.config.jar !== undefined) {
			const cookie = response.config.jar.toJSON().cookies.find((cookie) => cookie.key === "_checkout_queue_token");
			if (cookie !== undefined) {
				queueToken = cookie.value;
			} else {
				throw new Error("No queue token found for " + domain);
			}
		} else {
			throw new Error("No cookie jar found for " + domain);
		}

		return new ShopifyQueue(domain, client, queueToken);
	};

	static findAvailableVariant = (products: any[]): number | null => {
		for (const product of products) {
			for (const variant of product.variants) {
				if (variant.available) {
					return variant.id;
				}
			}
		}
		return null;
	};

	checkQueue = async () => {
		this.#lastChecked = this.getTimestamp();
		const payload = {
			query: "\n{\npoll(token: $token) {\ntoken\npollAfter\nqueueEtaSeconds\nproductVariantAvailability {\nid\navailable\n}\n}\n}\n",
			variables: {
				token: this.#lastQueueToken,
			},
		};

		let response;
		try {
			response = await this.#client.post("queue/poll", payload);
		} catch (error) {
			throw new Error("Axios error on polling queue for " + this.#domain);
		}
		if (response.status !== 200) {
			throw new Error("Unable to poll queue for " + this.#domain);
		}
		this.#queue = response.data.data.poll.queueEtaSeconds;
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
		return Math.floor(Date.now() / 1000);
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

	getSiteQueues = async (): Promise<ShopifyQueue[]> => {
		for await (const site of this.#sites) {
			await site.checkQueue();
			console.log("last checked", site.lastChecked, site.domain, "queue length", site.queue);
		}
		return this.#sites;
	};

	get sites(): ShopifyQueue[] {
		return this.#sites;
	}
}

// (async () => {
// 	const driver = await QueueDriver.initialize([
// 		"https://kith.com",
// 		"https://dtlr.com/products/234234",
// 		"https://shoepalace.com",
// 		"https://www.socialstatuspgh.com/",
// 	]);
// 	setInterval(async () => {
// 		await driver.getSiteQueues();
// 	}, 5000);
// })();

export { QueueDriver, ShopifyQueue };
