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

        let response: Response;
        try {
            response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`, {
                signal: controller.signal,
                headers: { 'Add-Padding': 'true' }
            });
        } finally {
            clearTimeout(timeoutId);
        }

        if (!response.ok) {
            throw new Error(`HIBP API returned ${response.status}`);
        }

        const text = await response.text();
        const lines = text.split(/\r?\n/);

        for (const line of lines) {
            const separator = line.indexOf(':');
            if (separator < 0) continue;
            const h = line.slice(0, separator).trim().toUpperCase();
            const count = Number.parseInt(line.slice(separator + 1).trim(), 10);
            if (h === suffix && Number.isFinite(count)) {
                return { breached: true, count };
            }
        }

        return { breached: false, count: 0 };
    } catch (error) {
        console.error("Error checking password breach:", error);
        // A failed lookup is not evidence that the password is safe.
        throw new Error('Breach check unavailable; try again later.');
    }
}
