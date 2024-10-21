# LicenseLynx for Java

For Java, use the ``map`` method from the ``LicenseLynx`` class to achieve the same functionality.

## Usage

```java
import com.siemens.LicenseLynx;

public class LicenseExample {
    public static void main(String[] args) {
        // Map the license name
        LicenseObject licenseObject = LicenseLynx.map("licenseName");
        System.out.println(licenseObject.getCanonical());
        System.out.println(licenseObject.getSrc());
    }
}
```
