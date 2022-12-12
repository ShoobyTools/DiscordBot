interface Variant {
    size: string;
    variant: number;
    quantity?: number;
}

interface ProductVariants {
    title: string;
    url: string;
    image: string;
    variants: Variant[];
    hasQuantity: boolean;
    totalQuantity?: number;
}

export { Variant, ProductVariants };