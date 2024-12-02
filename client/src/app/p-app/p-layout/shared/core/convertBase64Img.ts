import { DomSanitizer, SafeUrl } from "@angular/platform-browser";

export const convertBase64ToImg = (base64Str: string): string => {
    const byteCharacters = atob(base64Str);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/webp' });
    const url = URL.createObjectURL(blob);
    return url;
}