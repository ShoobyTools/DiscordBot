import axios, { AxiosResponse } from "axios";
import { ProductVariants } from "../types/product";
import { load } from "cheerio";
import { headers } from "../common/requests";

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
		return resp.data;
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
// atmosStock("https://www.atmosusa.com/products/nike-dunk-low-special-edition-kentucky-white-varsity-royal");
export {getVariants, atmosStock};
