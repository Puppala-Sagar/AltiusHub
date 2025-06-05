// 🧑‍💻 Intern (0–1 Years Experience) 
// A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.
// Given a string s, return true if it is a palindrome, or false otherwise.

// Example 1:
// Input: s = "A man, a plan, a canal: Panama"
// Output: true
// Explanation: "amanaplanacanalpanama" is a palindrome.

// Example 2:
// Input: s = "race a car"
// Output: false
// Explanation: "raceacar" is not a palindrome.

// Example 3:
// Input: s = " "
// Output: true
// Explanation: s is an empty string "" after removing non-alphanumeric characters.
// Since an empty string reads the same forward and backward, it is a palindrome.
//  
// Constraints:
// 1 <= s.length <= 2 * 105
// s consists only of printable ASCII characters.
// Focus Areas:	
// String manipulation
// Two-pointer technique
// Time complexity analysis


import java.util.*;

public class Solution1 {
    static public boolean isPalindrome(String s) {

        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");

        int left = 0;
        int right = cleaned.length() - 1;
        
        while (left < right) {
            if (cleaned.charAt(left) != cleaned.charAt(right)) {
                return false; 
            }
            left++;
            right--;
        }
        
        return true; 
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String s=sc.nextLine();

        System.out.println(isPalindrome(s));
    }
}
