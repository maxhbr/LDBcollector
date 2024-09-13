# LicenseLynx for Java

For Java, use the ``map`` method from the ``LicenseLynx`` class to achieve the same functionality.

## Usage

```javascript
import com.siemens.LicenseLynx;

public class LicenseExample {
    public static void main(String[] args) {
        // Map the license name
        String canonicalName = LicenseLynx.map("licenseName");
        System.out.println(canonicalName);
    }
}
```
