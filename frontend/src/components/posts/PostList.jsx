import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import PostCard from "./PostCard";
import api from "../../services/api";

export default function PostList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    pages: 0,
    currentPage: 1,
    perPage: 10,
  });

  const page = parseInt(searchParams.get("page")) || 1;
  const category = searchParams.get("category") || "";
  const tag = searchParams.get("tag") || "";
  const search = searchParams.get("search") || "";

  useEffect(() => {
    fetchPosts();
  }, [page, category, tag, search]);

  const fetchPosts = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        page,
        per_page: 10,
        status: "published",
      };

      if (category) params.category = category;
      if (tag) params.tag = tag;
      if (search) params.search = search;

      const response = await api.get("/posts", { params });

      setPosts(response.data.posts);
      setPagination({
        total: response.data.total,
        pages: response.data.pages,
        currentPage: response.data.current_page,
        perPage: response.data.per_page,
      });
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load posts");
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    const params = new URLSearchParams(searchParams);
    params.set("page", newPage.toString());
    setSearchParams(params);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading posts...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <button onClick={fetchPosts} className="btn-primary">
          Try Again
        </button>
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="empty-state">
        <h2>No posts found</h2>
        <p>There are no published posts yet. Check back later!</p>
      </div>
    );
  }

  return (
    <div className="post-list-container">
      <div className="post-list">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {pagination.pages > 1 && (
        <div className="pagination">
          <button
            onClick={() => handlePageChange(pagination.currentPage - 1)}
            disabled={pagination.currentPage === 1}
            className="btn-secondary"
          >
            Previous
          </button>

          <span className="pagination-info">
            Page {pagination.currentPage} of {pagination.pages}
          </span>

          <button
            onClick={() => handlePageChange(pagination.currentPage + 1)}
            disabled={pagination.currentPage === pagination.pages}
            className="btn-secondary"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
