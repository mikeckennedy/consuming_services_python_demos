using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace tooled_blog_consumer
{
	class Program
	{
		static void Main(string[] args)
		{
			var client = new svc.Blog();
			var posts = client.AllPosts();
			Console.WriteLine("All blog posts:");
			foreach (var post in posts)
			{
				Console.WriteLine("* {0} has {1:N0} of views.", post.Title, post.ViewCount);
			}
		}
	}
}
