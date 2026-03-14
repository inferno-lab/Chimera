export const fontFamily: string;
export const fontImport: string;

export interface TypeRole {
  fontVariationSettings: string;
  fontSize: number;
  letterSpacing?: string;
}

export const type: Record<string, TypeRole>;

export function fv(wght: number, MONO: number, CASL: number, slnt?: number): string;

export function applyType(role: keyof typeof type): {
  fontFamily: string;
  fontVariationSettings: string;
  fontSize: number;
  letterSpacing?: string;
};
