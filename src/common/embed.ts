import { ShopifyQueue } from "../modules/queue";

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

export { queueMonitorEmbed }