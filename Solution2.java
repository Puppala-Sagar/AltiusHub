// 🧑‍💻 Intern (0–1 Years Experience) 
// Given an integer array nums, return the length of the longest strictly increasing subsequence. Come up with an algorithm that runs in O(n log(n)) time complexity

// Example 1:
// Input: nums = [10,9,2,5,3,7,101,18]
// Output: 4
// Explanation: The longest increasing subsequence is [2,3,7,101], therefore the length is 4.

// Example 2:
// Input: nums = [0,1,0,3,2,3]
// Output: 4

// Example 3:
// Input: nums = [7,7,7,7,7,7,7]
// Output: 1
//  
// Constraints:
// 1 <= nums.length <= 2500
// -104 <= nums[i] <= 104
// Focus Areas:
// Dynamic Programming
// Binary Search
// Time and space optimisation


import java.util.*;


class Solution2{

    static int lengthOfLIS(int[] nums) {
        if (nums.length == 0) return 0;

        int[] dp = new int[nums.length];
        Arrays.fill(dp, 1); 

        for (int i = 1; i < nums.length; i++) {
            for (int j = 0; j < i; j++) {
                if (nums[i] > nums[j]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
        }

        int maxLength = 0;
        for (int length : dp) {
            maxLength = Math.max(maxLength, length);
        }

        return maxLength;
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        String s= sc.nextLine();
        String[] parts = s.split(",");
        int n = parts.length;
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) {
            if(i==0 && parts[i].startsWith("[")) {
                parts[i] = parts[i].substring(1); 
                nums[i]=Integer.parseInt(parts[i]);
                continue;
            }
            else if (i==n-1 && parts[i].endsWith("]")) {
                parts[i] = parts[i].substring(0, parts[i].length() - 1); 
            }
            nums[i] = Integer.parseInt(parts[i]);
        }

        // System.out.println(Arrays.toString(nums));
        
        System.out.println(lengthOfLIS(nums));
    }
}