import java.util.Scanner;

public class Mileage {
    public static void main(String[] args) {
        int miles;
        double gallons, mpg;

        Scanner s = new Scanner(System.in);

        System.out.println("Enter miles and gallons: ");
        miles = s.nextInt();
        gallons = s.nextDouble();

        mpg = miles / gallons;

      
        System.out.println("Miles Per Gallon: " + mpg);
    }
}
