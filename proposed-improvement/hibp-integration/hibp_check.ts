/**
 * HIBP k-anonymity check via Web Crypto API.
 */
export async function checkPasswordBreach(password: string): Promise<{breached: boolean, count: number}> {
    if (!password) {
        return { breached: false, count: 0 };
    }

    try {
        // Encode password to Uint8Array
        const encoder = new TextEncoder();
        const data = encoder.encode(password);

        // Compute SHA-1 hash
        const hashBuffer = await crypto.subtle.digest('SHA-1', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();

        const prefix = hashHex.slice(0, 5);
        const suffix = hashHex.slice(5);

        // Fetch using k-anonymity
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 sec timeout

        const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HIBP API returned ${response.status}`);
        }

        const text = await response.text();
        const lines = text.split('\n');

        for (const line of lines) {
            const [h, count] = line.split(':');
            if (h.trim() === suffix) {
                return { breached: true, count: parseInt(count.trim(), 10) };
            }
        }

        return { breached: false, count: 0 };
    } catch (error) {
        console.error("Error checking password breach:", error);
        // Fail open: assume not breached if API fails
        return { breached: false, count: 0 };
    }
}
