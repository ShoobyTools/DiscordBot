import axios, { AxiosResponse } from "axios";
import { ProductVariants } from "../types/product";
import { load } from "cheerio";

const headers = {
	accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"accept-encoding": "gzip, deflate",
	"accept-language": "en-US,en;q=0.9",
	dnt: "1",
	"sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
	"sec-ch-ua-mobile": "?0",
	"sec-ch-ua-platform": '"Windows"',
	"sec-fetch-dest": "document",
	"sec-fetch-mode": "navigate",
	"sec-fetch-site": "none",
	"sec-fetch-user": "?1",
	"upgrade-insecure-requests": "1",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
};

const getVariants = async (url: string) => {
	let resp: AxiosResponse;
	try {
		resp = await axios.get(`${url.replace(/.variant=.*/, "")}.json`, { headers: headers });
	} catch (error) {
		if (axios.isAxiosError(error)) {
			throw new Error("Axios error getting StockX product: " + error);
		} else {
			throw new Error("Unexpected error getting StockX product: " + error);
		}
	}

	if (resp.status == 200) {
		console.log(resp.data);
	}
};

const atmosStock = async (url: string) => {
	if (!url.includes("atmosusa.com")) {
		throw new Error("Unsupported URL. atmosUSA only.");
	}

	let resp: AxiosResponse;
	try {
		resp = await axios.get(url, { headers: headers });
	} catch (error) {
		if (axios.isAxiosError(error) && error!.response!.status === 404) {
			throw new Error("Product not found.");
		} else {
			throw new Error("Error getting atmosUSA product: " + error);
		}
	}

	let $;
	if (resp.status === 200) {
		$ = load(resp.data);
	} else {
		throw new Error("Error loading atmosUSA product page. Response code: " + resp.status);
	}

	if ($ === undefined) {
		throw new Error("Error loading product HTML into Cheerio object");
	}

	const productData: string | null = $('script[type="application/json"][data-product-json]').html();

	let data;
	if (productData !== null) {
		data = JSON.parse(productData);
	} else {
		throw new Error("No product data found");
	}

	const results = [];
	const variants = data.product.variants;
	const inventory = data.inventories;

	for (const variant in inventory) {
		const size = variants.find((v: any) => v.id == variant).title;
		results.push({
			variant: variant,
			size: size,
			stock: Math.abs(inventory[variant].inventory_quantity),
		});
	}

	return results;
};

// getVariants("https://www.shoepalace.com/products/jordan-dd0587-141-air-jordan-5-retro-concord-mens-lifestyle-shoes-white-blue?variant=41233584193742");
atmosStock("https://www.atmosusa.com/products/nike-dunk-low-special-edition-kentucky-white-varsity-royal");
