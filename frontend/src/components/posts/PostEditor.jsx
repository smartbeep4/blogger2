import { useState, useEffect, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import { useAuth } from "../../context/AuthContext";
import { useAutosave } from "../../hooks/useAutosave";
import api from "../../services/api";

export default function PostEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  const [formData, setFormData] = useState({
    title: "",
    content: "",
    excerpt: "",
    featured_image_url: "",
    category_ids: [],
    tag_ids: [],
    status: "draft",
  });

  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newTagName, setNewTagName] = useState("");
  const [creatingCategory, setCreatingCategory] = useState(false);
  const [creatingTag, setCreatingTag] = useState(false);

  // Autosave function
  const autosaveContent = useCallback(
    async (content) => {
      if (id && content) {
        await api.post(`/posts/${id}/autosave`, {
          title: formData.title,
          content: content,
        });
      }
    },
    [id, formData.title],
  );

  // Autosave status
  const { status: autosaveStatus } = useAutosave(
    autosaveContent,
    formData.content,
    2000,
  );

  // Load post data if editing
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load categories and tags
        const [categoriesRes, tagsRes] = await Promise.all([
          api.get("/categories"),
          api.get("/tags"),
        ]);

        setCategories(categoriesRes.data.categories);
        setTags(tagsRes.data.tags);

        // Load post if editing
        if (id) {
          const postRes = await api.get(`/posts/by-id/${id}`);
          const post = postRes.data.post;

          // Check if autosave exists
          try {
            const autosaveRes = await api.get(`/posts/${id}/autosave`);
            const autosave = autosaveRes.data.autosave;

            // Ask user if they want to restore autosaved content
            if (autosave && confirm("Restore autosaved content?")) {
              setFormData({
                ...post,
                title: autosave.title || post.title,
                content: autosave.content,
                category_ids: post.categories?.map((c) => c.id) || [],
                tag_ids: post.tags?.map((t) => t.id) || [],
              });
            } else {
              setFormData({
                ...post,
                category_ids: post.categories?.map((c) => c.id) || [],
                tag_ids: post.tags?.map((t) => t.id) || [],
              });
            }
          } catch {
            // No autosave, use post data
            setFormData({
              ...post,
              category_ids: post.categories?.map((c) => c.id) || [],
              tag_ids: post.tags?.map((t) => t.id) || [],
            });
          }
        }
      } catch (error) {
        setErrors({ general: "Failed to load data" });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleContentChange = (value) => {
    setFormData((prev) => ({ ...prev, content: value }));
  };

  const handleMultiSelect = (e, field) => {
    const options = Array.from(e.target.selectedOptions);
    const values = options.map((opt) => parseInt(opt.value));
    setFormData((prev) => ({ ...prev, [field]: values }));
  };

  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) return;
    setCreatingCategory(true);
    try {
      const response = await api.post("/categories", { name: newCategoryName.trim() });
      const newCategory = response.data.category;
      setCategories([...categories, newCategory]);
      setFormData((prev) => ({
        ...prev,
        category_ids: [...prev.category_ids, newCategory.id],
      }));
      setNewCategoryName("");
    } catch (error) {
      alert(error.response?.data?.error || "Failed to create category");
    } finally {
      setCreatingCategory(false);
    }
  };

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;
    setCreatingTag(true);
    try {
      const response = await api.post("/tags", { name: newTagName.trim() });
      const newTag = response.data.tag;
      setTags([...tags, newTag]);
      setFormData((prev) => ({
        ...prev,
        tag_ids: [...prev.tag_ids, newTag.id],
      }));
      setNewTagName("");
    } catch (error) {
      alert(error.response?.data?.error || "Failed to create tag");
    } finally {
      setCreatingTag(false);
    }
  };

  const handleSubmit = async (e, publishNow = false) => {
    e.preventDefault();
    setSaving(true);
    setErrors({});

    try {
      // Build data object, only including optional fields if they have values
      const data = {
        title: formData.title,
        content: formData.content,
        status: publishNow ? "published" : formData.status,
        category_ids: formData.category_ids,
        tag_ids: formData.tag_ids,
      };

      // Only include optional fields if they have values
      if (formData.excerpt) {
        data.excerpt = formData.excerpt;
      }
      if (formData.featured_image_url) {
        data.featured_image_url = formData.featured_image_url;
      }

      if (id) {
        await api.put(`/posts/${id}`, data);
      } else {
        const response = await api.post("/posts", data);
        navigate(`/posts/${response.data.post.id}/edit`);
        return;
      }

      navigate("/dashboard");
    } catch (error) {
      setErrors({
        general: error.response?.data?.error || "Failed to save post",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  const quillModules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ list: "ordered" }, { list: "bullet" }],
      ["blockquote", "code-block"],
      [{ align: [] }],
      ["link", "image"],
      ["clean"],
    ],
  };

  return (
    <div className="post-editor-container">
      <div className="editor-header">
        <h1>{id ? "Edit Post" : "New Post"}</h1>
        <div className="autosave-status">
          {autosaveStatus === "saving" && (
            <span className="status-saving">Saving...</span>
          )}
          {autosaveStatus === "saved" && (
            <span className="status-saved">Saved ✓</span>
          )}
          {autosaveStatus === "error" && (
            <span className="status-error">Save failed ✗</span>
          )}
        </div>
      </div>

      {errors.general && (
        <div className="form-error general-error">{errors.general}</div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            className="form-input"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="content">Content</label>
          <ReactQuill
            theme="snow"
            value={formData.content}
            onChange={handleContentChange}
            modules={quillModules}
            className="quill-editor"
          />
        </div>

        <div className="form-group">
          <label htmlFor="excerpt">Excerpt (Optional)</label>
          <textarea
            id="excerpt"
            name="excerpt"
            className="form-input"
            rows="3"
            value={formData.excerpt}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="featured_image_url">
            Featured Image URL (Optional)
          </label>
          <input
            type="url"
            id="featured_image_url"
            name="featured_image_url"
            className="form-input"
            value={formData.featured_image_url}
            onChange={handleChange}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="category_ids">Categories</label>
            <select
              id="category_ids"
              multiple
              className="form-input"
              value={formData.category_ids}
              onChange={(e) => handleMultiSelect(e, "category_ids")}
            >
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            <div className="inline-create">
              <input
                type="text"
                placeholder="New category name"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleCreateCategory())}
                disabled={creatingCategory}
              />
              <button
                type="button"
                onClick={handleCreateCategory}
                disabled={creatingCategory || !newCategoryName.trim()}
                className="btn btn-outline btn-sm"
              >
                {creatingCategory ? "..." : "Add"}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="tag_ids">Tags</label>
            <select
              id="tag_ids"
              multiple
              className="form-input"
              value={formData.tag_ids}
              onChange={(e) => handleMultiSelect(e, "tag_ids")}
            >
              {tags.map((tag) => (
                <option key={tag.id} value={tag.id}>
                  {tag.name}
                </option>
              ))}
            </select>
            <div className="inline-create">
              <input
                type="text"
                placeholder="New tag name"
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleCreateTag())}
                disabled={creatingTag}
              />
              <button
                type="button"
                onClick={handleCreateTag}
                disabled={creatingTag || !newTagName.trim()}
                className="btn btn-outline btn-sm"
              >
                {creatingTag ? "..." : "Add"}
              </button>
            </div>
          </div>
        </div>

        <div className="editor-actions">
          <button type="submit" className="btn-secondary" disabled={saving}>
            {saving ? "Saving..." : "Save Draft"}
          </button>

          <button
            type="button"
            onClick={(e) => handleSubmit(e, true)}
            className="btn-primary"
            disabled={saving}
          >
            {saving ? "Publishing..." : "Publish"}
          </button>

          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="btn-outline"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
