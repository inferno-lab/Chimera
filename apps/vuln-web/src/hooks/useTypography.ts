import { type, fontFamily } from '../lib/type-system';

export const useTypography = (role: keyof typeof type) => {
  const typeRole = type[role];
  return {
    style: {
      fontFamily,
      fontVariationSettings: typeRole.fontVariationSettings,
      fontSize: `${typeRole.fontSize}px`,
      ...(typeRole.letterSpacing && { letterSpacing: typeRole.letterSpacing }),
    },
  };
};
