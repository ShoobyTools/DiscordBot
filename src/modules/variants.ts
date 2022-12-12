import axios, { AxiosResponse } from "axios";
import { ProductVariants, Variant } from "../types/product";
import { load } from "cheerio";
import { headers } from "../common/requests";
import { parseDomain } from "../common/tools";

const getVariants = async (url: string): Promise<ProductVariants> => {
	const domain = parseDomain(url);
	// custom domain checks
	if (domain === "atmosusa.com") {
		return atmosStock(url);
	}

	let resp: AxiosResponse;
	try {
		resp = await axios.get(`${url.replace(/\?variant=.*/, "")}.json`, { headers: headers });
	} catch (error) {
		if (axios.isAxiosError(error) && error!.response!.status === 404) {
			throw new Error("Product is not loaded");
		} else {
			throw new Error("Unexpected error getting StockX product: " + error);
		}
	}

	let product;
	if (resp.status == 200) {
		product = resp.data.product;
	}

	const hasQuantity = "inventory_quantity" in product.variants[0];
	let totalQuantity = 0;
	let vars: Variant[];
	if (hasQuantity) {
		vars = product.variants.map((variant: any) => {
			const quantity = Math.abs(variant.inventory_quantity);
			totalQuantity += quantity;
			return {
				size: variant.title,
				variant: variant.id,
				quantity: quantity,
			};
		});
	} else {
		vars = product.variants.map((variant: any) => {
			return {
				size: variant.title,
				variant: variant.id,
			};
		});
	}

	return {
		title: product.title,
		url: url,
		image: product.images[0].src,
		variants: vars,
		hasQuantity: hasQuantity,
		totalQuantity: totalQuantity,
	};
};

// atmos loads quantity data from within the HTML so extra work is required
const atmosStock = async (url: string): Promise<ProductVariants> => {
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

	const vars: Variant[] = [];
	const variants = data.product.variants;
	const inventory = data.inventories;
	let totalQuantity = 0;
	for (const variant in inventory) {
		const size = variants.find((v: any) => v.id == variant).title;
		const quantity = Math.abs(inventory[variant].inventory_quantity);
		totalQuantity += quantity;
		vars.push({
			size: size,
			variant: Number(variant),
			quantity: quantity,
		});
	}

	return {
		title: data.product.title,
		url: url,
		image: data.product.images[0].startsWith("//") ? `https:${data.product.images[0]}` : data.product.images[0],
		variants: vars,
		hasQuantity: true,
		totalQuantity: totalQuantity,
	};
};

export { getVariants };
