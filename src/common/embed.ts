import { ShopifyQueue } from "../modules/queue";
import { ProductVariants } from "../types/product";
import { getFaviconUrl, parseDomain } from "./tools";

const queueMonitorEmbed = (queue: ShopifyQueue) => {
    return {
        color: 0x0099ff,
        title: `${queue.domain}`,
        description: 'Queue monitor',
        thumbnail: {
            url: queue.icon,
        },
        fields: [
            {
                name: 'Current length',
                value: `${queue.queue} seconds`,
                inline: false,
            },
            {
                name: 'Expected pass time',
                value: `<T:${queue.expectedPassTime}>`,
                inline: false,
            },
        ],
        footer: {
            text: `Last checked <T:${queue.lastChecked}>`,
        },
    };
}

const variantsEmbed = (product: ProductVariants) => {
    const fields = [{
        name: 'Sizes',
        value: `\`\`\`\n${product.variants.map((variant) => variant.size).join('\n')}\`\`\``,
        inline: true,
    }];

    if (product.hasQuantity) {
        fields.push({
            name: 'Stock',
            value: `\`\`\`md\n${product.variants.map((variant) => variant.quantity === 0 ? "* " : variant.quantity).join('\n')}\`\`\``,
            inline: true,
        });
    }

    fields.push({
        name: 'Variants',
        value: `\`\`\`\n${product.variants.map((variant) => variant.variant).join('\n')}\`\`\``,
        inline: true,
    });

    if (product.hasQuantity) {
        fields.push({
            name: 'Total stock',
            value: `\`\`\`\n${product.totalQuantity}\`\`\``,
            inline: false,
        });
    }

    const domain = parseDomain(product.url);

    return {
        color: 0x0099ff,
        title: product.title,
        url: product.url,
        author: {
            name: domain,
            icon_url: getFaviconUrl(domain),
            url: product.url,
        },
        thumbnail: {
            url: product.image,
        },
        fields: fields,
        footer: {
            text: `Shopify Variants`,
        }
    };
};

export { queueMonitorEmbed, variantsEmbed }