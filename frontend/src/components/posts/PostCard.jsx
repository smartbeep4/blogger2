import { Link } from "react-router-dom";

export default function PostCard({ post }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <article className="post-card">
      {post.featured_image_url && (
        <div className="post-card-image">
          <img src={post.featured_image_url} alt={post.title} />
        </div>
      )}

      <div className="post-card-content">
        <div className="post-card-meta">
          <span className="post-author">
            By {post.author?.display_name || post.author?.username}
          </span>
          <span className="post-date">
            {formatDate(post.published_at || post.created_at)}
          </span>
        </div>

        <h2 className="post-card-title">
          <Link to={`/posts/${post.slug}`}>{post.title}</Link>
        </h2>

        {post.excerpt && <p className="post-card-excerpt">{post.excerpt}</p>}

        <div className="post-card-footer">
          <div className="post-categories">
            {post.categories?.map((category) => (
              <span key={category.id} className="category-badge">
                {category.name}
              </span>
            ))}
          </div>

          <div className="post-tags">
            {post.tags?.slice(0, 3).map((tag) => (
              <span key={tag.id} className="tag-badge">
                #{tag.name}
              </span>
            ))}
          </div>
        </div>

        <Link to={`/posts/${post.slug}`} className="post-read-more">
          Read more →
        </Link>
      </div>
    </article>
  );
}
