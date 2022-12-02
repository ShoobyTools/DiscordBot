interface Variant {
    size: string;
    variant: number;
    quantity: number;
}

interface ProductVariants {
    title: string;
    sku: string;
    url: string;
    image: string;
    retailPrice: number;
    variants: Variant[];
    totalQuantity: number;
}

export { ProductVariants };